import csv
import html
import zipfile
from pathlib import Path
from statistics import mean

base_dir = Path(__file__).resolve().parent
logs_dir = base_dir / 'logs'
log_csv = logs_dir / 'log.csv'
if not log_csv.exists():
    log_csv = logs_dir / 'logs.csv'

rows = list(csv.DictReader(log_csv.open(newline='', encoding='utf-8')))

def num(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

def avg_for(event_type):
    values = [num(r.get('duration_sec')) for r in rows if r.get('type') == event_type]
    return round(mean(values), 4) if values else 0.0

def nonzero_avg(column):
    values = [num(r.get(column)) for r in rows]
    nz = [v for v in values if v > 0]
    return (round(mean(nz), 4), len(nz)) if nz else (0.0, 0)

count_encryption = len([r for r in rows if r.get('type') == 'encryption'])
count_share = len([r for r in rows if r.get('type') == 'share'])
count_download = len([r for r in rows if r.get('type') == 'download'])
count_decryption = len([r for r in rows if r.get('type') == 'decryption'])

avg_encrypt = avg_for('encryption')
avg_share = avg_for('share')
avg_download = avg_for('download')
avg_decrypt = avg_for('decryption')

upload_plain_avg, upload_plain_n = nonzero_avg('upload_time_plain_sec')
upload_enc_avg, upload_enc_n = nonzero_avg('upload_time_encrypted_sec')
download_plain_avg, download_plain_n = nonzero_avg('download_time_plain_sec')
download_enc_avg, download_enc_n = nonzero_avg('download_time_encrypted_sec')

sizes = [int(float(r.get('file_size', 0))) for r in rows if str(r.get('file_size', '')).strip()]
min_size = min(sizes) if sizes else 0
max_size = max(sizes) if sizes else 0

report_lines = [
    'Week 4 Report: Security and Performance Data Collection',
    '',
    'Project Context',
    'This report summarizes the Week 4 data collection process for the secure cloud file sharing system. The system combines encryption, user-specific sharing, access control, and sender-controlled key distribution while tracking performance impacts.',
    '',
    'What Makes This System Unique',
    'The system is unique because it combines strong security controls with operational performance measurement in one workflow:',
    '1) AES/Fernet-based file encryption before sharing',
    '2) User-specific sharing and access control',
    '3) Sender-controlled key inclusion for recipients',
    '4) Structured logging of security and performance events in CSV format',
    '',
    'Data Collection Procedure (Week 4)',
    '1) Upload file through the web interface and automatically encrypt server-side.',
    '2) System generates file_id at upload and stores metadata.',
    '3) Share file with recipient and optionally include decryption key.',
    '4) Download file and perform decryption using provided key.',
    '5) For each operation, write structured records into logs/log.csv.',
    '6) Analyze timing and size fields to compare security overhead vs throughput.',
    '',
    'Current Dataset Snapshot',
    f'Total records analyzed: {len(rows)}',
    f'Event counts: encryption={count_encryption}, share={count_share}, download={count_download}, decryption={count_decryption}',
    f'Average event duration (sec): encryption={avg_encrypt}, share={avg_share}, download={avg_download}, decryption={avg_decrypt}',
    f'Upload time plain documents (sec): non-zero samples={upload_plain_n}, average={upload_plain_avg}',
    f'Upload time encrypted documents (sec): non-zero samples={upload_enc_n}, average={upload_enc_avg}',
    f'Download time plain documents (sec): non-zero samples={download_plain_n}, average={download_plain_avg}',
    f'Download time encrypted documents (sec): non-zero samples={download_enc_n}, average={download_enc_avg}',
    f'Observed file size range (bytes): min={min_size}, max={max_size}',
    '',
    'Variation Analysis',
    '1) Encryption impact on speed: encryption adds compute and integrity processing overhead before network/storage completion, so upload-related elapsed time generally increases compared with plain handling.',
    '2) File size impact: processing time and transfer time rise with file size because more bytes must be encrypted, authenticated, written, read, and transmitted.',
    '3) Download variance: encrypted and plain download times can be close for very small files where fixed I/O and framework overhead dominate.',
    '4) Authentication attempts in logs: current persistent CSV is focused on file operations. For richer Week 5 analysis, auth success/failure events should be appended to CSV using consistent fields (event_type=auth_login/auth_failure, username, timestamp, duration).',
    '',
    'Why Encryption Affects Upload Time (Evidence-Based Explanation)',
    'Encryption affects upload time because the server performs additional operations before data is finalized:',
    '1) Symmetric encryption transforms plaintext into ciphertext block-by-block (or stream-equivalent), adding CPU work [1].',
    '2) Authenticated encryption/message authentication adds integrity checks, which adds computation and metadata handling [2].',
    '3) Encrypted payload formats can increase byte size (headers/IV/timestamp/MAC), increasing write/transfer workload [2][3].',
    '4) End-to-end secure transport and cryptographic primitives consume CPU cycles and can reduce throughput under load [4].',
    '',
    'Log Formatting Improvements Implemented',
    'The CSV now uses stable columns that simplify later statistical analysis and plotting:',
    'file_id, file_type, file_size, type, duration_sec, owner, date_shared, time_shared, upload_time_plain_sec, upload_time_encrypted_sec, download_time_plain_sec, download_time_encrypted_sec.',
    '',
    'Conclusion',
    'Week 4 confirms the design goal: security controls are integrated with measurable performance indicators. This supports objective analysis of trade-offs between confidentiality/integrity and operational speed in a cloud file-sharing context.',
    '',
    'References',
    '[1] NIST SP 800-38A, Recommendation for Block Cipher Modes of Operation, 2001.',
    '[2] Cryptography Project, Fernet (symmetric authenticated cryptography) documentation: https://cryptography.io/en/latest/fernet/',
    '[3] Fernet Specification: https://github.com/fernet/spec/blob/master/Spec.md',
    '[4] RFC 8446, The Transport Layer Security (TLS) Protocol Version 1.3, IETF, 2018.'
]

def make_document_xml(lines):
    paragraphs = []
    for line in lines:
        text = html.escape(line)
        if line == '':
            paragraphs.append('<w:p/>')
        else:
            paragraphs.append(
                '<w:p><w:r><w:t xml:space="preserve">' + text + '</w:t></w:r></w:p>'
            )

    body = ''.join(paragraphs) + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>'
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:o="urn:schemas-microsoft-com:office:office" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
        'xmlns:v="urn:schemas-microsoft-com:vml" '
        'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:w10="urn:schemas-microsoft-com:office:word" '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
        'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
        'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
        'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
        'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 wp14">'
        '<w:body>' + body + '</w:body></w:document>'
    )

content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
'''

rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
'''

out_path = base_dir / 'Week4docx.docx'
with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    zf.writestr('[Content_Types].xml', content_types)
    zf.writestr('_rels/.rels', rels)
    zf.writestr('word/document.xml', make_document_xml(report_lines))

print(f'Created: {out_path}')
