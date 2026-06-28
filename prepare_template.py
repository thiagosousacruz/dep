import re

with open('template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace sidebar SQL items
html = re.sub(
    r'(<div class="nav-section-title"><span>SQL</span> <span class="badge">\d+</span></div>).*?(<div class="nav-section">)',
    r'\1\n    {{ SIDEBAR_SQL }}\n  </div>\n  \2',
    html, flags=re.DOTALL
)

# Replace sidebar PySpark items
html = re.sub(
    r'(<div class="nav-section-title"><span>PySpark</span> <span class="badge">\d+</span></div>).*?(<div style="padding:\.75rem 1rem)',
    r'\1\n    {{ SIDEBAR_PYSPARK }}\n  </div>\n  \2',
    html, flags=re.DOTALL
)

# Replace main content sections
# They start after <section id="home"> ... </section>
# And go until <footer>
html = re.sub(
    r'(</section>\s*<!-- ==================================================================================\s*--.*?)(<footer>)',
    r'</section>\n\n  {{ CONTENT_INJECT }}\n\n\2',
    html, flags=re.DOTALL
)

with open('template.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Template prepared.")
