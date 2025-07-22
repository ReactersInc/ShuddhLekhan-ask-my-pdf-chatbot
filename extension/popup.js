const API_URL = 'http://localhost:5000/web/summarize-url';

document.getElementById('summarize').addEventListener('click', () => {
  const summaryEl = document.getElementById('summary');
  const loadingEl = document.getElementById('loading');
  summaryEl.textContent = '';
  loadingEl.style.display = 'block';

  chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
    chrome.tabs.sendMessage(
      tabs[0].id,
      { type: 'GET_PAGE_URL' },
      response => {
        const pageUrl = response?.url;
        if (!pageUrl) {
          summaryEl.textContent = 'Could not get page URL.';
          loadingEl.style.display = 'none';
          return;
        }
        fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: pageUrl })
        })
          .then(res => res.json())
          .then(data => {
            summaryEl.textContent = data.summary || data.error || 'No summary returned.';
          })
          .catch(err => {
            console.error(err);
            summaryEl.textContent = 'Error calling summarizer.';
          })
          .finally(() => { loadingEl.style.display = 'none'; });
      }
    );
  });
});