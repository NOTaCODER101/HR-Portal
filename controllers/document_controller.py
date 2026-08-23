"""
controllers/document_controller.py
==================================
Upload, download, and delete employee documents.
"""
import os
from flask import Blueprint, request, redirect, url_for, flash, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import DocumentService
from services.exceptions import HRPortalBaseError
from models.user import User
from dao.document_dao import DocumentDAO
from utils.auth_utils import role_required

document_bp = Blueprint('document', __name__)
document_service = DocumentService()
document_dao = DocumentDAO()

@document_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Normally, you might allow HR to upload for someone else. 
    # Here we assume the user is uploading their own document, or HR is uploading.
    employee_id = int(request.form.get('employee_id', user.employee.id if (user and user.employee) else 0))
    
    if not employee_id:
        flash("Invalid employee context for upload.", "danger")
        return redirect(request.referrer or url_for('dashboard.index'))

    # Security check: Only the employee themselves or HR Admin can upload
    if (not user or user.role != 'HR Admin') and (not user or not user.employee or user.employee.id != employee_id):
        flash("You are not authorized to upload documents for this employee.", "danger")
        return redirect(request.referrer or url_for('dashboard.index'))

    if 'document' not in request.files:
        flash("No file part in the request.", "danger")
        return redirect(request.referrer or url_for('dashboard.index'))

    file = request.files['document']
    doc_type = request.form.get('document_type', 'Other')

    try:
        document_service.upload_employee_document(employee_id, file, doc_type, user_id)
        flash("Document uploaded successfully.", "success")
    except HRPortalBaseError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash("An error occurred during file upload.", "danger")

    return redirect(request.referrer or url_for('employee.profile', employee_id=employee_id))


@document_bp.route('/<int:document_id>/download', methods=['GET'])
@jwt_required()
def download(document_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.employee:
        flash("You are not registered as an employee.", "danger")
        return redirect(url_for('dashboard.index'))

    doc = document_dao.get_by_id(document_id)

    if not doc:
        flash("Document not found.", "danger")
        return redirect(request.referrer or url_for('dashboard.index'))

    # Security check: User must be HR Admin or the owner of the document
    if (not user or user.role != 'HR Admin') and (not user or not user.employee or user.employee.id != doc.employee_id):
        flash("You do not have permission to download this document.", "danger")
        return redirect(request.referrer or url_for('dashboard.index'))

    directory = os.path.dirname(doc.file_path)
    filename = os.path.basename(doc.file_path)

    # Use send_from_directory for secure file serving
    return send_from_directory(directory, filename, as_attachment=True)


@document_bp.route('/<int:document_id>/delete', methods=['POST'])
@jwt_required()
@role_required('HR Admin')
def delete(document_id):
    try:
        document_service.delete_employee_document(document_id)
        flash("Document deleted successfully.", "success")
    except HRPortalBaseError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash("An error occurred while deleting the document.", "danger")

    return redirect(request.referrer or url_for('dashboard.index'))
