console.log('✅ content.js loaded');

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === 'GET_PAGE_URL') {
    sendResponse({ url: window.location.href });
    return true; 
  }
});