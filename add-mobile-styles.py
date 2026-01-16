#!/usr/bin/env python3
import os
import re
import glob

# Mobile CSS for index.html
INDEX_MOBILE_CSS = """
        /* ===== MOBILE RESPONSIVE ===== */
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            
            .header { 
                padding: 1.5rem 1rem; 
                border-radius: 12px;
            }
            .header h1 { font-size: 1.5rem; }
            .header .subtitle { font-size: 1rem; }
            .meta { gap: 0.5rem; }
            .meta-item { 
                font-size: 0.75rem; 
                padding: 0.4rem 0.8rem;
            }
            .logo svg { width: 100px; height: 25px; }
            
            .stats-bar {
                grid-template-columns: repeat(2, 1fr);
                padding: 1rem;
                gap: 0.75rem;
            }
            .stat-value { font-size: 1.5rem; }
            .stat-label { font-size: 0.75rem; }
            .info-btn { width: 14px; height: 14px; font-size: 9px; }
            .tooltip {
                width: 200px;
                font-size: 0.75rem;
                padding: 0.5rem 0.75rem;
                left: auto;
                right: -10px;
                transform: none;
            }
            .tooltip::after {
                left: auto;
                right: 15px;
            }
            
            .view-toggle { 
                flex-direction: row;
                width: 100%;
                padding: 0.35rem;
            }
            .view-btn { 
                padding: 0.6rem 1rem; 
                font-size: 0.8rem;
                flex: 1;
                justify-content: center;
            }
            .view-btn svg { width: 16px; height: 16px; }
            
            .section-title { font-size: 1.2rem; }
            
            .reports-grid { 
                grid-template-columns: 1fr; 
                gap: 1rem;
            }
            .report-card { 
                padding: 1.25rem;
                border-radius: 12px;
            }
            .report-card h3 { font-size: 1rem; }
            .report-card p { font-size: 0.85rem; }
            .card-date { 
                font-size: 0.65rem;
                padding: 0.2rem 0.5rem;
            }
            .badge { 
                font-size: 0.65rem; 
                padding: 0.2rem 0.6rem;
            }
            .featured-badge { font-size: 0.6rem; }
            
            .date-separator { margin: 2rem 0 1rem; }
            .date-badge { 
                font-size: 0.75rem; 
                padding: 0.4rem 1rem;
            }
            .date-badge .count { font-size: 0.65rem; }
            
            .version-legend { padding: 1rem; }
            .version-legend h3 { font-size: 0.9rem; }
            .version-legend-items { 
                flex-direction: column; 
                gap: 1rem;
            }
            .version-legend-item { font-size: 0.8rem; }
            
            .footer { 
                padding: 1.5rem 1rem; 
                font-size: 0.85rem;
            }
        }
        
        @media (max-width: 480px) {
            .container { padding: 0.75rem; }
            .header { padding: 1.25rem 1rem; }
            .header h1 { font-size: 1.3rem; }
            .header .subtitle { font-size: 0.9rem; }
            .meta-item { font-size: 0.7rem; padding: 0.35rem 0.7rem; }
            
            .stats-bar { 
                grid-template-columns: 1fr 1fr;
                gap: 0.5rem;
            }
            .stat { padding: 0.5rem; }
            .stat-value { font-size: 1.3rem; }
            .stat-label { font-size: 0.7rem; }
            
            .view-btn { padding: 0.5rem 0.75rem; font-size: 0.75rem; }
            
            .report-card { padding: 1rem; }
            .report-card h3 { font-size: 0.95rem; }
        }
"""

# Mobile CSS for report pages
REPORT_MOBILE_CSS = """
        /* ===== MOBILE RESPONSIVE ===== */
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            
            .header { 
                padding: 1.5rem 1rem; 
                border-radius: 12px;
            }
            .header h1 { font-size: 1.4rem; line-height: 1.3; }
            .header-meta { gap: 1rem; }
            .meta-item { font-size: 0.8rem; }
            .logo svg { width: 100px; height: 25px; }
            
            .card { 
                padding: 1.25rem; 
                border-radius: 12px;
                margin-bottom: 1rem;
            }
            .card h2 { font-size: 1.25rem; }
            .card h3 { font-size: 1.05rem; }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
                gap: 0.75rem;
            }
            .stat-card { padding: 1rem; }
            .stat-value { font-size: 1.75rem; }
            .stat-label { font-size: 0.8rem; }
            
            table { font-size: 0.85rem; }
            th, td { padding: 0.75rem 0.5rem; }
            
            .finding-card { padding: 1rem; }
            .finding-card h4 { font-size: 1rem; }
            
            ul, ol { padding-left: 1.25rem; }
            li { font-size: 0.9rem; margin-bottom: 0.5rem; }
            
            .badge { font-size: 0.7rem; padding: 0.25rem 0.6rem; }
            
            .download-btn {
                bottom: 15px;
                right: 15px;
                padding: 12px 16px;
                font-size: 0.85rem;
            }
            
            .back-link {
                font-size: 0.85rem;
                padding: 0.5rem 1rem;
            }
            
            .footer { padding: 1.5rem 1rem; font-size: 0.85rem; }
        }
        
        @media (max-width: 480px) {
            .container { padding: 0.75rem; }
            .header { padding: 1.25rem 0.75rem; }
            .header h1 { font-size: 1.2rem; }
            .meta-item { font-size: 0.75rem; }
            
            .card { padding: 1rem; }
            .card h2 { font-size: 1.1rem; }
            .card h3 { font-size: 0.95rem; }
            
            .stats-grid { grid-template-columns: 1fr 1fr; }
            .stat-card { padding: 0.75rem; }
            .stat-value { font-size: 1.5rem; }
            
            /* Make tables scrollable on very small screens */
            .table-wrapper {
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
            table { min-width: 500px; }
            
            .download-btn {
                bottom: 10px;
                right: 10px;
                padding: 10px 14px;
                font-size: 0.8rem;
            }
        }
        
        /* Touch-friendly improvements */
        @media (pointer: coarse) {
            .download-btn { padding: 14px 20px; }
            .back-link { padding: 0.6rem 1.2rem; }
            a, button { min-height: 44px; }
        }
"""

def update_index():
    """Update index.html with mobile styles"""
    filepath = '/tmp/assisterr-research/index.html'
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Remove old incomplete mobile styles
    content = re.sub(
        r'@media \(max-width: 768px\) \{[^}]+\}',
        '',
        content
    )
    
    # Insert new mobile styles before </style>
    if '/* ===== MOBILE RESPONSIVE =====' not in content:
        content = content.replace('</style>', INDEX_MOBILE_CSS + '\n    </style>')
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"✅ Updated: index.html")

def update_reports():
    """Update all report HTML files with mobile styles"""
    files = glob.glob('/tmp/assisterr-research/*.html')
    
    for filepath in files:
        if 'index.html' in filepath:
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Skip if already has mobile styles
        if '/* ===== MOBILE RESPONSIVE =====' in content:
            print(f"⏭️  Skipped (already has mobile): {os.path.basename(filepath)}")
            continue
        
        # Wrap tables in scrollable wrapper for mobile
        content = re.sub(
            r'(<table[^>]*>)',
            r'<div class="table-wrapper">\1',
            content
        )
        content = re.sub(
            r'(</table>)',
            r'\1</div>',
            content
        )
        
        # Insert mobile styles before </style>
        content = content.replace('</style>', REPORT_MOBILE_CSS + '\n    </style>')
        
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Updated: {os.path.basename(filepath)}")

if __name__ == '__main__':
    print("📱 Adding mobile responsiveness to all files...\n")
    update_index()
    update_reports()
    print("\n✨ Done! All files are now mobile-friendly.")
