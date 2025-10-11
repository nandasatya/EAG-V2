document.addEventListener('DOMContentLoaded', () => {
  const tweetsDiv = document.getElementById('tweets');

  chrome.storage.local.get(['tweets'], (result) => {
    const tweets = result.tweets || [];

    if (tweets.length === 0) {
      tweetsDiv.textContent = 'No tweets found.  Please wait a moment for the extension to fetch them, or check your API key.';
      return;
    }

    tweets.forEach(tweet => {
      const tweetElement = document.createElement('div');
      tweetElement.classList.add('tweet');

      const userElement = document.createElement('div');
      userElement.classList.add('user');
      userElement.textContent = `@${tweet.user}`;
      tweetElement.appendChild(userElement);

      const textElement = document.createElement('p');
      textElement.textContent = tweet.text;
      tweetElement.appendChild(textElement);

      tweetsDiv.appendChild(tweetElement);
    });
  });
});