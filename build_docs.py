import os
import re
import markdown
from bs4 import BeautifulSoup

TEMPLATE_PATH = 'template.html'
OUTPUT_PATH = 'index.html'

def process_markdown_file(filepath, index, prefix, color_class, file_to_id_map):
    with open(filepath, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract title from first heading
    title_match = re.search(r'^#\s+(.+)', md_content, flags=re.MULTILINE)
    if not title_match:
        title_match = re.search(r'^##\s+(.+)', md_content, flags=re.MULTILINE)
    
    full_title = title_match.group(1).strip() if title_match else os.path.basename(filepath)
    # Generate a short search string
    search_tags = re.sub(r'[^a-zA-Z0-9\s]', '', full_title).lower()
    
    # Convert markdown to html
    # Extensions: fenced_code, tables
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables'])
    
    # Process HTML to match the specific playbook styling
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Convert first h1 or h2 into the specific cheat-section header
    h_tags = soup.find_all(['h1', 'h2'])
    if h_tags:
        main_h = h_tags[0]
        new_h2 = soup.new_tag('h2')
        span_num = soup.new_tag('span', attrs={'class': f'sec-num {color_class}'})
        num_str = f"{index:02d}"
        span_num.string = f"{prefix} {num_str}"
        new_h2.append(span_num)
        new_h2.append(f" {full_title.replace(prefix + ' ', '')}")
        main_h.replace_with(new_h2)
        
    # Replace internal links (.md to #section-id)
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        if href and href in file_to_id_map:
            a_tag['href'] = file_to_id_map[href]
    
    # Wrap pre > code blocks with specific div
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        if code:
            lang_class = code.get('class', [''])[0]
            if lang_class.startswith('language-'):
                lang = lang_class.replace('language-', '')
            else:
                lang = 'sql' if prefix == 'SQL' else 'python'
            
            # Create wrapper
            wrap_div = soup.new_tag('div', attrs={'class': 'code-wrap'})
            
            # Create lang div
            lang_div = soup.new_tag('div', attrs={'class': f'color_class-lang'})
            lang_div['class'] = f'code-lang {color_class}-lang'
            lang_div.string = lang.upper()
            
            # Create copy btn
            copy_btn = soup.new_tag('button', attrs={'class': 'copy-btn', 'onclick': 'copyCode(this)'})
            copy_btn.string = "📋 Copiar"
            
            # Move pre inside wrapper
            pre_copy = soup.new_tag('pre')
            pre_copy.string = code.get_text() # we don't need the code tag inside pre for this playbook styling
            
            wrap_div.append(lang_div)
            wrap_div.append(copy_btn)
            wrap_div.append(pre_copy)
            
            pre.replace_with(wrap_div)
            
    # Wrap in section
    section_id = f"{prefix.lower()}-{index:02d}"
    section_html = f'<section id="{section_id}" class="cheat-section">\n{str(soup)}\n</section>'
    
    # Create sidebar item
    nav_item = f'<a class="nav-item {color_class}-item" href="#{section_id}" data-search="{search_tags}"><span class="num">{index:02d}</span>{full_title}</a>'
    
    return section_html, nav_item

def build():
    folders = [
        ('01_cheatsheets/01_sql', 'SQL', 'sql'),
        ('01_cheatsheets/02_pyspark', 'PySpark', 'pyspark')
    ]
    
    # First pass: map filenames to section IDs
    file_to_id_map = {}
    for folder_path, prefix, color_class in folders:
        if not os.path.exists(folder_path):
            continue
        files = [f for f in os.listdir(folder_path) if f.endswith('.md') and not f.lower() == 'readme.md']
        files.sort()
        for idx, filename in enumerate(files, 1):
            section_id = f"#{prefix.lower()}-{idx:02d}"
            file_to_id_map[filename] = section_id

    # Second pass: process files
    all_content = []
    sidebar_sql = []
    sidebar_pyspark = []
    
    for folder_path, prefix, color_class in folders:
        if not os.path.exists(folder_path):
            continue
            
        files = [f for f in os.listdir(folder_path) if f.endswith('.md') and not f.lower() == 'readme.md']
        files.sort()
        
        for idx, filename in enumerate(files, 1):
            filepath = os.path.join(folder_path, filename)
            section_html, nav_item = process_markdown_file(filepath, idx, prefix, color_class, file_to_id_map)
            all_content.append(section_html)
            
            if prefix == 'SQL':
                sidebar_sql.append(nav_item)
            else:
                sidebar_pyspark.append(nav_item)
                
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()
        
    template = template.replace('{{ SIDEBAR_SQL }}', '\n    '.join(sidebar_sql))
    template = template.replace('{{ SIDEBAR_PYSPARK }}', '\n    '.join(sidebar_pyspark))
    template = template.replace('{{ CONTENT_INJECT }}', '\n\n'.join(all_content))
    
    # Update badges
    template = re.sub(r'(<span>SQL</span> <span class="badge">)\d+(</span>)', f'\\g<1>{len(sidebar_sql)}\\g<2>', template)
    template = re.sub(r'(<span>PySpark</span> <span class="badge">)\d+(</span>)', f'\\g<1>{len(sidebar_pyspark)}\\g<2>', template)
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(template)
        
    print("Build successful. index.html has been generated with mapped internal links.")

if __name__ == '__main__':
    build()
