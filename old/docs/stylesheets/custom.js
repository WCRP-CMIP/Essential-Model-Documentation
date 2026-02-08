// Essential Model Documentation - Custom Scripts for shadcn theme

// Configuration
const CONFIG = {
  repoUrl: 'https://github.com/WCRP-CMIP/Essential-Model-Documentation',
  repoName: 'WCRP-CMIP/Essential-Model-Documentation',
  customLinks: [
    { title: 'CMIP Website', url: 'https://wcrp-cmip.org/' },
    { title: 'WCRP', url: 'https://www.wcrp-climate.org/' }
  ]
};

// Run on load and after delay
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM loaded, running init...');
  init();
  setTimeout(init, 300);
  setTimeout(init, 1000);
});

function init() {
  console.log('Init running...');
  setupHeaderControls();
  setupCollapsibleNav();
  buildNestedNavigation();
  addCustomLinks();
  updateFooter();
  addVersionSelector();
  setupHeaderAnchors();
  fixCopyPageButton();
  setupGlobalCopyHandler();
  setupTabbedContent();
}

// ============================================
// FIX COPY PAGE BUTTON
// ============================================

function fixCopyPageButton() {
  // Find the copy page button (has "Copy Page" text or copy icon)
  const copyButtons = document.querySelectorAll('button[onclick*="clipboard"]');
  
  copyButtons.forEach(btn => {
    if (btn.dataset.copyFixed) return;
    btn.dataset.copyFixed = 'true';
    
    // Remove the broken onclick handler
    btn.removeAttribute('onclick');
    
    // Add working click handler
    btn.addEventListener('click', async function(e) {
      e.preventDefault();
      
      try {
        // Get the article content as text
        const article = document.querySelector('article');
        if (!article) {
          console.error('No article found to copy');
          return;
        }
        
        // Get text content, preserving some structure
        const content = article.innerText || article.textContent;
        
        // Add footer with attribution
        const contentWithFooter = appendCopyFooter(content);
        
        // Copy to clipboard
        await navigator.clipboard.writeText(contentWithFooter);
        
        // Visual feedback
        const span = btn.querySelector('span');
        if (span) {
          span.textContent = 'Copied!';
        }
        
        setTimeout(() => {
          if (span) {
            span.textContent = 'Copy Page';
          }
        }, 2000);
        
        console.log('Page content copied to clipboard');
      } catch (err) {
        console.error('Failed to copy:', err);
      }
    });
  });
}

/**
 * Append attribution footer to copied content
 */
function appendCopyFooter(content) {
  const currentUrl = window.location.href.split('?')[0]; // Remove any existing query params
  const embedUrl = currentUrl + (currentUrl.includes('?') ? '&' : '?') + 'embed=true';
  const timestamp = new Date().toISOString().replace('T', ' ').split('.')[0] + ' UTC';
  
  const footer = `

---
This content was copied from ${currentUrl} at ${timestamp}.
Use of content is protected by a CC-BY-4.0 licence and external use is allowed at your own risk.

If you wish to embed a live version of this page please use: ${embedUrl}

Iframe example:
<iframe src="${embedUrl}" width="100%" height="600" frameborder="0"></iframe>
`;
  
  return content + footer;
}

/**
 * Setup global copy handler - ensures it's only added once
 */
function setupGlobalCopyHandler() {
  if (window.copyHandlerSetup) return;
  window.copyHandlerSetup = true;
  
  // Use capturing phase to ensure we catch the event
  document.addEventListener('copy', function(e) {
    console.log('Copy event triggered');
    const selection = window.getSelection().toString();
    console.log('Selection length:', selection.length);
    
    // Only add footer if copying substantial content (more than 100 chars)
    if (selection && selection.length > 100) {
      e.preventDefault();
      const contentWithFooter = appendCopyFooter(selection);
      e.clipboardData.setData('text/plain', contentWithFooter);
      console.log('Copy intercepted, footer added');
    }
  }, true); // Use capture phase
  
  console.log('Global copy handler installed');
}

// Install copy handler immediately (don't wait for DOMContentLoaded)
setupGlobalCopyHandler();

// ============================================
// HEADER CONTROLS
// ============================================

function setupHeaderControls() {
  // Disabled - was interfering with sidebar Home link
  // The GitHub link is already in the header by default
  console.log('Header controls disabled to preserve Home link');
  return;
}

// ============================================
// COLLAPSIBLE NAVIGATION (shadcn structure)
// ============================================

function setupCollapsibleNav() {
  const groups = document.querySelectorAll('[data-slot="sidebar-group"]');
  
  console.log('Setting up collapsible navigation for', groups.length, 'groups');
  
  groups.forEach((group, index) => {
    const label = group.querySelector('[data-slot="sidebar-group-label"]');
    const content = group.querySelector('[data-slot="sidebar-group-content"]');
    
    // If there's no label, this is the root group (Home, Contributors) - keep it expanded always
    if (!label) {
      console.log(`Group ${index}: ROOT GROUP (no label), keeping expanded`);
      if (content) {
        content.style.display = 'block';
        content.style.visibility = 'visible';
        content.style.opacity = '1';
        content.style.maxHeight = 'none';
      }
      return;
    }
    
    if (!content) return;
    
    // Already processed?
    if (label.dataset.collapsibleSetup === 'done') return;
    label.dataset.collapsibleSetup = 'done';
    
    const groupName = label.textContent.trim();
    
    // Add classes for styling
    label.classList.add('nav-collapsible');
    content.classList.add('nav-children');
    
    // Check if any link in this group is active
    const checkForActivePage = (element) => {
      const links = element.querySelectorAll('a[data-slot="sidebar-menu-button"]');
      for (const link of links) {
        if (link.getAttribute('data-active') === 'true') {
          return true;
        }
      }
      return false;
    };
    
    const containsCurrentPage = checkForActivePage(content);
    
    // Set initial state based on whether it contains current page
    const initiallyExpanded = containsCurrentPage;
    
    if (initiallyExpanded) {
      label.classList.add('expanded');
      content.classList.remove('collapsed');
      content.style.maxHeight = '2000px';
      content.style.opacity = '1';
      content.style.pointerEvents = 'auto';
      console.log(`Group ${index} "${groupName}": EXPANDED (contains active page)`);
    } else {
      label.classList.remove('expanded');
      content.classList.add('collapsed');
      content.style.maxHeight = '0';
      content.style.opacity = '0';
      content.style.pointerEvents = 'none';
      console.log(`Group ${index} "${groupName}": COLLAPSED`);
    }
    
    // Click handler for toggle - works for ALL groups
    label.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const isExpanded = label.classList.contains('expanded');
      
      console.log(`Toggling "${groupName}": currently ${isExpanded ? 'expanded' : 'collapsed'}`);
      
      if (isExpanded) {
        // Collapse
        label.classList.remove('expanded');
        content.classList.add('collapsed');
        content.style.maxHeight = '0';
        content.style.opacity = '0';
        content.style.pointerEvents = 'none';
        console.log(`  → Now COLLAPSED`);
      } else {
        // Expand
        label.classList.add('expanded');
        content.classList.remove('collapsed');
        content.style.maxHeight = '2000px';
        content.style.opacity = '1';
        content.style.pointerEvents = 'auto';
        console.log(`  → Now EXPANDED`);
      }
    });
  });
  
  // Ensure root-level menu items stay visible
  const rootMenuItems = document.querySelectorAll('[data-slot="sidebar-menu"] > [data-slot="sidebar-menu-item"]');
  rootMenuItems.forEach(item => {
    item.style.display = 'block';
    item.style.visibility = 'visible';
    item.style.opacity = '1';
  });
  
  console.log('Collapsible nav setup complete');
}

// ============================================
// CUSTOM LINKS
// ============================================

function addCustomLinks() {
  if (!CONFIG.customLinks || CONFIG.customLinks.length === 0) return;
  if (document.querySelector('.custom-links-section')) return;
  
  // Find sidebar content area
  const sidebarContent = document.querySelector('[data-slot="sidebar-content"]');
  
  console.log('Sidebar content found:', !!sidebarContent);
  
  if (!sidebarContent) return;
  
  const section = document.createElement('div');
  section.className = 'custom-links-section';
  section.innerHTML = `
    <div class="custom-links-title">External Links</div>
    <div class="custom-links-list">
      ${CONFIG.customLinks.map(link => `
        <a href="${link.url}" class="custom-link" target="_blank" rel="noopener">
          <span>${link.title}</span>
        </a>
      `).join('')}
    </div>
  `;
  
  sidebarContent.appendChild(section);
  console.log('Custom links added');
}

// ============================================
// HEADER ANCHORS
// ============================================

function setupHeaderAnchors() {
  const content = document.querySelector('article, main, .content');
  if (!content) return;
  
  content.querySelectorAll('h1[id], h2[id], h3[id], h4[id], h5[id], h6[id]').forEach(header => {
    if (header.dataset.anchorSetup) return;
    header.dataset.anchorSetup = 'true';
    
    header.style.cursor = 'pointer';
    header.addEventListener('click', function(e) {
      if (e.target.tagName === 'A') return;
      window.location.hash = header.id;
      navigator.clipboard?.writeText(window.location.href.split('#')[0] + '#' + header.id);
    });
  });
}

// ============================================
// FOOTER
// ============================================

function updateFooter() {
  // Hide the shadcn footer entirely
  const shadcnFooter = document.querySelector('footer');
  if (shadcnFooter) {
    shadcnFooter.style.display = 'none';
  }
  
  // Check if we already added our footer
  if (document.querySelector('.md-footer')) return;
  
  // Find the bottom navigation (prev/next links)
  const bottomNav = document.querySelector('.mx-auto.flex.flex-wrap.h-16');
  
  // Create Material-style footer
  const footer = document.createElement('footer');
  footer.className = 'md-footer';
  
  // Get prev/next info from existing links
  const prevLink = bottomNav?.querySelector('a:first-of-type');
  const nextLink = bottomNav?.querySelector('a:last-of-type');
  
  let footerHTML = '<nav class="md-footer__inner">';
  
  if (prevLink && prevLink !== nextLink) {
    const prevTitle = prevLink.querySelector('span')?.textContent || prevLink.textContent.trim();
    const prevHref = prevLink.getAttribute('href');
    footerHTML += `
      <a href="${prevHref}" class="md-footer__link md-footer__link--prev" aria-label="Previous: ${prevTitle}">
        <div class="md-footer__button md-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M20 11v2H8l5.5 5.5-1.42 1.42L4.16 12l7.92-7.92L13.5 5.5 8 11z"></path>
          </svg>
        </div>
        <div class="md-footer__title">
          <span class="md-footer__direction">Previous</span>
          <div class="md-ellipsis">${prevTitle}</div>
        </div>
      </a>
    `;
  }
  
  if (nextLink) {
    const nextTitle = nextLink.querySelector('span')?.textContent || nextLink.textContent.trim();
    const nextHref = nextLink.getAttribute('href');
    footerHTML += `
      <a href="${nextHref}" class="md-footer__link md-footer__link--next" aria-label="Next: ${nextTitle}">
        <div class="md-footer__title">
          <span class="md-footer__direction">Next</span>
          <div class="md-ellipsis">${nextTitle}</div>
        </div>
        <div class="md-footer__button md-icon">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path d="M4 11v2h12l-5.5 5.5 1.42 1.42L19.84 12l-7.92-7.92L10.5 5.5 16 11z"></path>
          </svg>
        </div>
      </a>
    `;
  }
  
  footerHTML += '</nav>';
  footer.innerHTML = footerHTML;
  
  // Hide the original bottom nav
  if (bottomNav) {
    bottomNav.style.display = 'none';
  }
  
  // Insert footer before the shadcn footer or at end of main
  const main = document.querySelector('main');
  if (main) {
    main.appendChild(footer);
  }
  
  // Add attribution
  if (!document.querySelector('.footer-attribution')) {
    const attribution = document.createElement('div');
    attribution.className = 'footer-attribution';
    attribution.innerHTML = `
      <p>
        Built by <a href="https://github.com/wolfiex">Daniel Ellis</a>
        for <a href="https://wcrp-cmip.org">WCRP-CMIP</a>
        using the <a href="https://github.com/asiffer/mkdocs-shadcn">shadcn</a> theme.
      </p>
    `;
    document.body.appendChild(attribution);
  }
}

// ============================================
// VERSION SELECTOR
// ============================================

function addVersionSelector() {
  if (document.querySelector('.version-selector')) return;
  
  const baseUrl = typeof base_url !== 'undefined' 
    ? base_url 
    : window.location.pathname.split('/').slice(0, -2).join('/') + '/';
  
  fetch(baseUrl + '../versions.json')
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(versions => {
      if (!versions?.length) return;

      const pathParts = window.location.pathname.split('/').filter(p => p);
      const current = versions.find(v => 
        pathParts.includes(v.version) || v.aliases?.some(a => pathParts.includes(a))
      );

      const dropdown = document.createElement('div');
      dropdown.className = 'version-selector';
      dropdown.innerHTML = `
        <select id="version-select">
          ${versions.map(v => `
            <option value="${v.version}" ${current?.version === v.version ? 'selected' : ''}>
              ${v.aliases?.includes('latest') ? `${v.version} (latest)` : v.version}
            </option>
          `).join('')}
        </select>
      `;

      const header = document.querySelector('header');
      const target = header?.querySelector('.ml-auto') || header;
      target?.insertBefore(dropdown, target.firstChild);

      dropdown.querySelector('select').addEventListener('change', e => {
        const path = window.location.pathname;
        const pattern = current ? `(${current.version}|${current.aliases?.join('|') || ''})` : '';
        window.location.href = pattern 
          ? path.replace(new RegExp(`/${pattern}/`), `/${e.target.value}/`)
          : baseUrl + e.target.value + '/';
      });
    })
    .catch(() => {});
}

// Export for debugging
window.EMDCustom = { init, CONFIG };

// ============================================
// TABBED CONTENT SUPPORT
// ============================================

function setupTabbedContent() {
  const tabbedSets = document.querySelectorAll('.tabbed-set');
  
  tabbedSets.forEach(set => {
    // Skip if already set up
    if (set.dataset.tabbedSetup) return;
    set.dataset.tabbedSetup = 'true';
    
    const labels = set.querySelectorAll('.tabbed-labels > label');
    const inputs = set.querySelectorAll('input[type="radio"]');
    const blocks = set.querySelectorAll('.tabbed-content > .tabbed-block');
    
    // Function to update visible tab
    const updateTabs = () => {
      const checkedIndex = Array.from(inputs).findIndex(input => input.checked);
      
      // Update blocks
      blocks.forEach((block, index) => {
        if (index === checkedIndex) {
          block.style.display = 'block';
          block.style.visibility = 'visible';
          block.style.opacity = '1';
          block.setAttribute('data-active', 'true');
        } else {
          block.style.display = 'none';
          block.setAttribute('data-active', 'false');
        }
      });
      
      // Update labels
      labels.forEach((label, index) => {
        if (index === checkedIndex) {
          label.setAttribute('data-active', 'true');
        } else {
          label.setAttribute('data-active', 'false');
        }
      });
    };
    
    // Initial display
    updateTabs();
    
    // Add keyboard navigation and click handlers
    labels.forEach((label, index) => {
      label.setAttribute('tabindex', '0');
      label.setAttribute('role', 'tab');
      
      // Click handler
      label.addEventListener('click', () => {
        if (inputs[index]) {
          inputs[index].checked = true;
          updateTabs();
        }
      });
      
      // Keyboard handler
      label.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          if (inputs[index]) {
            inputs[index].checked = true;
            updateTabs();
          }
        }
        
        // Arrow key navigation
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
          e.preventDefault();
          const direction = e.key === 'ArrowLeft' ? -1 : 1;
          const newIndex = (index + direction + labels.length) % labels.length;
          labels[newIndex].focus();
          if (inputs[newIndex]) {
            inputs[newIndex].checked = true;
            updateTabs();
          }
        }
      });
      
      // Listen for radio button changes
      if (inputs[index]) {
        inputs[index].addEventListener('change', updateTabs);
      }
    });
    
    console.log('Tabbed content initialized:', labels.length, 'tabs');
  });
}


// ============================================
// BUILD NESTED NAVIGATION FROM SUMMARY.MD
// ============================================

async function buildNestedNavigation() {
  console.log('=== BUILDING NESTED NAVIGATION ===');
  
  if (window.nestedNavBuilt) {
    console.log('Already built, skipping');
    return;
  }
  window.nestedNavBuilt = true;
  
  try {
    const baseUrl = typeof base_url !== 'undefined' ? base_url : '/Essential-Model-Documentation/';
    const response = await fetch(baseUrl + 'SUMMARY.md');
    
    if (!response.ok) {
      console.log('Could not fetch SUMMARY.md');
      return;
    }
    
    const summaryText = await response.text();
    const navTree = parseSummary(summaryText);
    
    console.log('Navigation tree parsed, processing groups...');
    
    // Process each top-level group
    navTree.forEach(topItem => {
      if (topItem.type === 'group') {
        processGroupForNested(topItem, baseUrl);
      }
    });
    
    console.log('=== NESTED NAVIGATION COMPLETE ===');
  } catch (err) {
    console.error('Error building nested nav:', err);
  }
}

function parseSummary(text) {
  const lines = text.split('\n').filter(l => l.trim());
  const result = [];
  const stack = [{children: result, level: -1}];
  
  lines.forEach(line => {
    const match = line.match(/^(\s*)-\s+(.+)$/);
    if (!match) return;
    
    const indent = match[1].length;
    const content = match[2];
    const level = Math.floor(indent / 2);
    
    const linkMatch = content.match(/\[([^\]]+)\]\(([^)]+)\)/);
    const groupMatch = content.match(/^(.+):$/);
    
    let item;
    if (linkMatch) {
      item = {type: 'link', title: linkMatch[1], path: linkMatch[2], level};
    } else if (groupMatch) {
      item = {type: 'group', title: groupMatch[1], children: [], level};
    } else {
      return;
    }
    
    while (stack[stack.length - 1].level >= level) {
      stack.pop();
    }
    
    stack[stack.length - 1].children.push(item);
    
    if (item.type === 'group') {
      stack.push(item);
    }
  });
  
  return result;
}

function processGroupForNested(group, baseUrl) {
  const labels = document.querySelectorAll('[data-slot="sidebar-group-label"]');
  const matchingLabel = Array.from(labels).find(l => l.textContent.trim() === group.title + ':');
  
  if (!matchingLabel) return;
  
  const menu = matchingLabel.closest('[data-slot="sidebar-group"]')
    .querySelector('[data-slot="sidebar-menu"]');
  
  if (!menu) return;
  
  const nestedFolders = group.children.filter(c => c.type === 'group');
  
  console.log(`Group "${group.title}" has ${nestedFolders.length} nested folders`);
  
  nestedFolders.forEach(folder => {
    createNestedFolder(menu, folder, baseUrl);
  });
}

function createNestedFolder(parentMenu, folder, baseUrl) {
  const currentPath = window.location.pathname;
  
  const li = document.createElement('li');
  li.className = 'nested-folder-item';
  li.style.margin = '2px 0';
  
  // Folder header with arrow
  const header = document.createElement('div');
  header.className = 'nested-folder-toggle';
  header.innerHTML = `
    <span class="arrow" style="display: inline-block; width: 1rem; transition: transform 0.2s; font-size: 0.7rem;">▸</span>
    <span class="name">${folder.title}</span>
  `;
  header.style.cssText = `
    display: flex;
    align-items: center;
    padding: 0.5rem;
    cursor: pointer;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--emd-text-secondary);
    border-radius: 6px;
    transition: background 0.15s, color 0.15s;
  `;
  
  // Nested items container
  const container = document.createElement('ul');
  container.className = 'nested-folder-items';
  container.style.cssText = `
    list-style: none;
    padding: 0 0 0 1.5rem;
    margin: 0;
    max-height: 0;
    overflow: hidden;
    opacity: 0;
    transition: max-height 0.3s ease, opacity 0.2s ease;
  `;
  
  let hasActive = false;
  
  // Add child links
  folder.children.forEach(child => {
    if (child.type !== 'link') return;
    
    const itemLi = document.createElement('li');
    itemLi.style.margin = '0';
    
    const link = document.createElement('a');
    link.href = baseUrl + child.path.replace('.md', '/');
    link.textContent = child.title;
    link.style.cssText = `
      display: block;
      padding: 0.4rem 0.5rem;
      font-size: 0.75rem;
      color: var(--emd-text-secondary);
      text-decoration: none;
      border-radius: 4px;
      transition: all 0.15s;
    `;
    
    // Check if active
    const isActive = currentPath === link.href || currentPath.includes(link.href);
    if (isActive) {
      link.style.color = 'var(--emd-primary)';
      link.style.fontWeight = '600';
      hasActive = true;
    }
    
    link.addEventListener('mouseenter', () => {
      link.style.background = 'var(--emd-bg-secondary)';
      link.style.color = 'var(--emd-text)';
    });
    
    link.addEventListener('mouseleave', () => {
      link.style.background = 'transparent';
      link.style.color = isActive ? 'var(--emd-primary)' : 'var(--emd-text-secondary)';
    });
    
    itemLi.appendChild(link);
    container.appendChild(itemLi);
  });
  
  // Auto-expand if contains active page
  if (hasActive) {
    header.setAttribute('data-expanded', 'true');
    header.querySelector('.arrow').style.transform = 'rotate(90deg)';
    container.style.maxHeight = '1000px';
    container.style.opacity = '1';
  }
  
  // Toggle click handler
  header.addEventListener('click', () => {
    const expanded = header.getAttribute('data-expanded') === 'true';
    const arrow = header.querySelector('.arrow');
    
    if (expanded) {
      header.setAttribute('data-expanded', 'false');
      arrow.style.transform = 'rotate(0deg)';
      container.style.maxHeight = '0';
      container.style.opacity = '0';
    } else {
      header.setAttribute('data-expanded', 'true');
      arrow.style.transform = 'rotate(90deg)';
      container.style.maxHeight = '1000px';
      container.style.opacity = '1';
    }
  });
  
  // Hover effect
  header.addEventListener('mouseenter', () => {
    header.style.background = 'var(--emd-bg-secondary)';
    header.style.color = 'var(--emd-text)';
  });
  
  header.addEventListener('mouseleave', () => {
    header.style.background = 'transparent';
    header.style.color = 'var(--emd-text-secondary)';
  });
  
  li.appendChild(header);
  li.appendChild(container);
  parentMenu.appendChild(li);
  
  console.log(`  Created nested folder "${folder.title}" with ${folder.children.length} items`);
}
