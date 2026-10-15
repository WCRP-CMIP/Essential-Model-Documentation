document.addEventListener("DOMContentLoaded", function() {
    // Check if the user already made a choice (Accept or Deny)
    var cookies = document.cookie;
    if (cookies.indexOf('mtm_cookie_consent') > -1 || cookies.indexOf('mtm_consent_removed') > -1) {
        return; // Exit early if choice is already saved on this local machine
    }

    // Create the tiny floating box
    var banner = document.createElement('div');
    banner.id = 'matomo-cookie-banner';
    
    // Minimal styling for bottom-right placement
    banner.style.cssText = `
        position: fixed; 
        bottom: 12px; 
        right: 12px; 
        max-width: 240px;
        background: #ffffff; 
        color: #4b5563; 
        font-family: system-ui, -apple-system, sans-serif; 
        font-size: 10px; 
        padding: 8px 10px; 
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12);
        border: 1px solid #e4e4e7;
        z-index: 999999;
        display: flex;
        flex-direction: column;
        gap: 6px;
    `;

    // Tiny layout with Accept and Deny buttons
    banner.innerHTML = `
        <div>We use minimal cookies. <a href="/privacy-policy" style="color: #2563eb; text-decoration: underline;">Privacy Policy</a>.</div>
        <div style="display: flex; justify-content: flex-end; gap: 4px;">
            <button id="deny-cookies" style="background: transparent; color: #6b7280; border: 1px solid #d1d5db; padding: 2px 6px; font-size: 10px; cursor: pointer; border-radius: 2px;">Deny</button>
            <button id="accept-cookies" style="background: #2563eb; color: white; border: none; padding: 2px 6px; font-size: 10px; cursor: pointer; border-radius: 2px;">Accept</button>
        </div>
    `;

    document.body.appendChild(banner);

    // Accept Button Action
    document.getElementById('accept-cookies').addEventListener('click', function() {
        if (window._paq) {
            window._paq.push(['rememberCookieConsentGiven']); // Sets local mtm_cookie_consent cookie
        }
        banner.remove();
    });

    // Deny Button Action
    document.getElementById('deny-cookies').addEventListener('click', function() {
        if (window._paq) {
            window._paq.push(['rememberCookieConsentDismissed']); // Sets local mtm_consent_removed cookie
        }
        banner.remove();
    });
});
