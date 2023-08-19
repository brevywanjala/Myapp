function openCard(cardId) {
    var card = document.getElementById(cardId);
    var overlay = document.querySelector('.card-overlay');
    card.style.display = 'block';
    overlay.style.display = 'block';
  }
  
  function closeCard() {
    var cards = document.querySelectorAll('.card1');
    var overlay = document.querySelector('.card-overlay');
    for (var i = 0; i < cards.length; i++) {
      cards[i].style.display = 'none';
    }
    overlay.style.display = 'none';
  }

  const searchInput = document.getElementById('search-input');
  const videoContainer = document.getElementById('video-container');

  let debounceTimer;

  searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
          const searchQuery = searchInput.value.toLowerCase();
          fetch(`/?query=${searchQuery}`)
              .then(response => response.text())
              .then(videoData => {
                  const parser = new DOMParser();
                  const newHtml = parser.parseFromString(videoData, 'text/html');
                  const newVideoContainer = newHtml.getElementById('video-container');
                  // Replace the content of the existing video container
                  videoContainer.innerHTML = newVideoContainer.innerHTML;
              })
              .catch(error => {
                  console.error('Error fetching video data:', error);
                  videoContainer.innerHTML = '<p>Error fetching video data</p>';
              });
      }, 300); // Adjust the debounce time as needed
  });

