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
  addCustomLinks();
  updateFooter();
  addVersionSelector();
  setupHeaderAnchors();
}

// ============================================
// HEADER CONTROLS
// ============================================

function setupHeaderControls() {
  const header = document.querySelector('header');
  if (!header || header.querySelector('.header-repo')) return;
  
  const title = header.querySelector('h1, [data-slot="title"], .title, a[href="/"]');
  
  if (title && CONFIG.repoUrl) {
    const repoLink = document.createElement('a');
    repoLink.href = CONFIG.repoUrl;
    repoLink.className = 'header-repo';
    repoLink.target = '_blank';
    repoLink.rel = 'noopener';
    repoLink.textContent = CONFIG.repoName;
    
    if (title.tagName === 'A') {
      title.parentElement.replaceChild(repoLink, title);
    } else {
      title.innerHTML = '';
      title.appendChild(repoLink);
    }
  }
}

// ============================================
// COLLAPSIBLE NAVIGATION (shadcn structure)
// ============================================

function setupCollapsibleNav() {
  // shadcn uses data-slot="sidebar-group" for each section
  const groups = document.querySelectorAll('[data-slot="sidebar-group"]');
  
  console.log('Found sidebar groups:', groups.length);
  
  // Get current page path for matching
  const currentPath = window.location.pathname;
  
  groups.forEach(group => {
    const label = group.querySelector('[data-slot="sidebar-group-label"]');
    const content = group.querySelector('[data-slot="sidebar-group-content"]');
    
    if (!label || !content) return;
    
    // Already processed?
    if (label.dataset.collapsibleSetup === 'done') return;
    label.dataset.collapsibleSetup = 'done';
    
    // Add classes for styling
    label.classList.add('nav-collapsible');
    content.classList.add('nav-children');
    
    // Check if any link in this group is active (matches current page)
    const links = content.querySelectorAll('a[data-slot="sidebar-menu-button"]');
    let containsCurrentPage = false;
    
    links.forEach(link => {
      const isActive = link.getAttribute('data-active') === 'true';
      if (isActive) {
        containsCurrentPage = true;
      }
    });
    
    // Set initial state - collapsed unless contains current page
    if (containsCurrentPage) {
      label.classList.add('expanded');
      content.classList.remove('collapsed');
    } else {
      label.classList.remove('expanded');
      content.classList.add('collapsed');
    }
    
    // Click handler for toggle
    label.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const isExpanded = label.classList.contains('expanded');
      
      if (isExpanded) {
        label.classList.remove('expanded');
        content.classList.add('collapsed');
      } else {
        label.classList.add('expanded');
        content.classList.remove('collapsed');
      }
      
      console.log('Toggled group:', label.textContent.trim(), 'expanded:', !isExpanded);
    });
  });
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
