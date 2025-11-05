from flask import Flask, render_template, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from resume_parser import ResumeParser
from job_matcher import JobMatcher
import pandas as pd
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

EXCEL_FILE = 'data/all_resumes.xlsx'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400

    files = request.files.getlist('file')
    job_description = request.form.get('job_description', '')

    if not files or files[0].filename == '':
        return jsonify({'error': 'No files selected'}), 400

    results = []
    saved_count = 0
    rejected_count = 0

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)

            try:
                parser = ResumeParser()
                resume_data = parser.parse_resume(filepath)

                matcher = JobMatcher()
                match_score, matched_skills, missing_skills = matcher.calculate_match(
                    resume_data['skills'], job_description
                )

                excel_data = {
                    'Name': resume_data['name'],
                    'Email': resume_data['email'],
                    'Phone Number': resume_data['phone'],
                    'ATS Score': f"{match_score}%"
                }

                save_to_excel(excel_data)
                saved_count += 1
                status = "Saved"


                results.append({
                    'filename': filename,
                    'name': resume_data['name'],
                    'email': resume_data['email'],
                    'match_score': match_score,
                    'status': status,
                    'matched_skills': matched_skills,
                    'missing_skills': missing_skills
                })

                os.remove(filepath)

            except Exception as e:
                results.append({
                    'filename': filename,
                    'error': f'Error processing: {str(e)}',
                    'status': 'Error'
                })
                rejected_count += 1

                if os.path.exists(filepath):
                    os.remove(filepath)
        else:
            results.append({
                'filename': file.filename,
                'error': 'Invalid file type',
                'status': 'Rejected'
            })
            rejected_count += 1

    return jsonify({
        'success': True,
        'results': results,
        'summary': {
            'total_files': len(files),
            'saved_count': saved_count,
            'rejected_count': rejected_count,
            'message': f'Processed {len(files)} resumes: {saved_count} saved, {rejected_count} rejected'
        }
    })


def save_to_excel(data):
    """Save data to Excel with exact column structure"""
    try:
        columns = ['Name', 'Email', 'Phone Number', 'ATS Score']

        if os.path.exists(EXCEL_FILE):
            try:
                df_existing = pd.read_excel(EXCEL_FILE)

                if list(df_existing.columns) == columns:
                    duplicate_mask = df_existing['Email'] == data['Email']

                    if duplicate_mask.any():
                        df_existing.loc[duplicate_mask, 'ATS Score'] = data['ATS Score']
                        df_existing.loc[duplicate_mask, 'Name'] = data['Name']
                        df_existing.loc[duplicate_mask, 'Phone Number'] = data['Phone Number']
                        print(f"Updated existing resume for {data['Name']}")
                    else:
                        df_new = pd.DataFrame([data])
                        df_existing = pd.concat([df_existing, df_new], ignore_index=True)
                        print(f"Added new resume for {data['Name']}")

                    df_final = df_existing
                else:
                    print("Column mismatch detected, recreating Excel file...")
                    df_final = pd.DataFrame([data], columns=columns)

            except Exception as e:
                print(f"Error reading existing file: {e}, creating new one...")
                df_final = pd.DataFrame([data], columns=columns)
        else:
            df_final = pd.DataFrame([data], columns=columns)
            print(f"Created new Excel file with resume for {data['Name']}")

        df_final = df_final[columns]
        df_final.to_excel(EXCEL_FILE, index=False)
        print(f"Excel file updated: {EXCEL_FILE}")

    except Exception as e:
        print(f"Error saving to Excel: {e}")
        raise e


@app.route('/get_resumes')
def get_resumes():
    """Get all resumes data to display in web interface"""
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            resumes = df.to_dict('records')
            return jsonify({'success': True, 'resumes': resumes})
        else:
            return jsonify({'success': True, 'resumes': []})
    except Exception as e:
        return jsonify({'error': f'Error reading resumes: {str(e)}'}), 500


@app.route('/download')
def download_excel():
    """Download the Excel file with essential data - only when needed"""
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True, download_name='resume_shortlist.xlsx')
    return jsonify({'error': 'No resume data found'}), 404


@app.route('/stats')
def get_stats():
    """Get statistics about stored resumes"""
    try:
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            total_resumes = len(df)

            if 'ATS Score' in df.columns:
                scores = df['ATS Score'].astype(str).str.replace('%', '').astype(float)
                avg_score = scores.mean()
                high_scores = len(scores[scores >= 80])
            else:
                avg_score = 0
                high_scores = 0

            return jsonify({
                'total_resumes': total_resumes,
                'average_score': round(avg_score, 1),
                'high_score_count': high_scores,
                'excel_file': EXCEL_FILE
            })
        else:
            return jsonify({
                'total_resumes': 0,
                'average_score': 0,
                'high_score_count': 0,
                'excel_file': EXCEL_FILE
            })
    except Exception as e:
        return jsonify({'error': f'Error reading stats: {str(e)}'}), 500


@app.route('/clear', methods=['POST'])
def clear_resumes():
    try:
        if os.path.exists(EXCEL_FILE):
            os.remove(EXCEL_FILE)  # pura file hata do
        return jsonify({'success': True, 'message': 'All resume data cleared'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
