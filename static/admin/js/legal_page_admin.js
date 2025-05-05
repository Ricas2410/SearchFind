// JavaScript for Legal Page Admin

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the legal page admin
    if (document.getElementById('id_content')) {
        // Add a live preview functionality
        const contentField = document.getElementById('id_content');
        const previewDiv = document.querySelector('.legal-content-preview');
        
        if (contentField && previewDiv) {
            contentField.addEventListener('input', function() {
                previewDiv.innerHTML = this.value;
            });
        }
        
        // Add a button to insert common HTML elements
        const fieldset = contentField.closest('fieldset');
        if (fieldset) {
            const toolbar = document.createElement('div');
            toolbar.className = 'legal-page-toolbar';
            toolbar.style.marginBottom = '10px';
            
            // Add heading buttons
            ['H1', 'H2', 'H3'].forEach(function(tag) {
                const button = document.createElement('button');
                button.type = 'button';
                button.textContent = tag;
                button.style.marginRight = '5px';
                button.style.padding = '5px 10px';
                
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    insertAtCursor(contentField, `<${tag.toLowerCase()}>Heading</${tag.toLowerCase()}>`);
                });
                
                toolbar.appendChild(button);
            });
            
            // Add paragraph button
            const pButton = document.createElement('button');
            pButton.type = 'button';
            pButton.textContent = 'P';
            pButton.style.marginRight = '5px';
            pButton.style.padding = '5px 10px';
            
            pButton.addEventListener('click', function(e) {
                e.preventDefault();
                insertAtCursor(contentField, '<p>Paragraph text</p>');
            });
            
            toolbar.appendChild(pButton);
            
            // Add list buttons
            const ulButton = document.createElement('button');
            ulButton.type = 'button';
            ulButton.textContent = 'UL';
            ulButton.style.marginRight = '5px';
            ulButton.style.padding = '5px 10px';
            
            ulButton.addEventListener('click', function(e) {
                e.preventDefault();
                insertAtCursor(contentField, '<ul>\n  <li>List item 1</li>\n  <li>List item 2</li>\n</ul>');
            });
            
            toolbar.appendChild(ulButton);
            
            const olButton = document.createElement('button');
            olButton.type = 'button';
            olButton.textContent = 'OL';
            olButton.style.marginRight = '5px';
            olButton.style.padding = '5px 10px';
            
            olButton.addEventListener('click', function(e) {
                e.preventDefault();
                insertAtCursor(contentField, '<ol>\n  <li>List item 1</li>\n  <li>List item 2</li>\n</ol>');
            });
            
            toolbar.appendChild(olButton);
            
            // Insert the toolbar before the content field
            contentField.parentNode.insertBefore(toolbar, contentField);
        }
    }
});

// Helper function to insert text at cursor position
function insertAtCursor(field, text) {
    if (field.selectionStart || field.selectionStart === 0) {
        const startPos = field.selectionStart;
        const endPos = field.selectionEnd;
        field.value = field.value.substring(0, startPos) + text + field.value.substring(endPos, field.value.length);
        field.selectionStart = startPos + text.length;
        field.selectionEnd = startPos + text.length;
    } else {
        field.value += text;
    }
    
    // Trigger input event to update preview
    field.dispatchEvent(new Event('input'));
    
    field.focus();
}
