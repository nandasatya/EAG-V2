const users = ["karpathy"]; // Testing with just one user first
const bearerToken = "AAAAAAAAAAAAAAAAAAAAAOb04AEAAAAAKHTI6LfwUcslTwHIeUd4oLtufJY=IeP97TI0H7UnTDkyj6NhBjJR7U16vifFjPdeWAoSHMKqBqvzLr"; // Replace with your actual Bearer Token

const getTweets = async (user) => {
  console.log(`Fetching tweets for ${user}`);
  
  // First, get the user ID from username
  const userUrl = `https://api.twitter.com/2/users/by/username/${user}`;
  const userOptions = {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${bearerToken}`,
      'Content-Type': 'application/json',
    },
  };

  try {
    // Get user ID
    const userResponse = await fetch(userUrl, userOptions);
    
    if (!userResponse.ok) {
      console.error(`HTTP error getting user ID! status: ${userResponse.status} for user ${user}`);
      if (userResponse.status === 401) {
        console.error('Unauthorized - check your Bearer Token');
      } else if (userResponse.status === 429) {
        console.error('Rate limit exceeded - waiting before retry');
        chrome.storage.local.set({ 
          lastRateLimit: Date.now(),
          rateLimited: true 
        });
        return [];
      } else if (userResponse.status === 404) {
        console.error(`User ${user} not found`);
        return [];
      }
      return [];
    }
    
    const userData = await userResponse.json();
    console.log(`User data for ${user}:`, userData);
    
    if (!userData.data || !userData.data.id) {
      console.warn(`User not found: ${user}`, userData);
      return [];
    }
    
    const userId = userData.data.id;
    console.log(`Found user ID for ${user}: ${userId}`);
    
    // Now get tweets from user timeline
    const tweetsUrl = `https://api.twitter.com/2/users/${userId}/tweets?max_results=3&tweet.fields=created_at`;
    const tweetsOptions = {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${bearerToken}`,
        'Content-Type': 'application/json',
      },
    };
    
    const tweetsResponse = await fetch(tweetsUrl, tweetsOptions);
    
    if (!tweetsResponse.ok) {
      console.error(`HTTP error getting tweets! status: ${tweetsResponse.status} for user ${user}`);
      if (tweetsResponse.status === 401) {
        console.error('Unauthorized - check your Bearer Token');
      } else if (tweetsResponse.status === 429) {
        console.error('Rate limit exceeded - waiting before retry');
        chrome.storage.local.set({ 
          lastRateLimit: Date.now(),
          rateLimited: true 
        });
        return [];
      } else if (tweetsResponse.status === 403) {
        console.error('Forbidden - Your app may not have permission to access user tweets');
      } else if (tweetsResponse.status === 400) {
        console.error('Bad Request - API endpoint or parameters are incorrect');
        console.error('This might mean the user timeline endpoint requires higher permissions');
      }
      return [];
    }
    
    const tweetsData = await tweetsResponse.json();
    console.log(`Tweets data for ${user}:`, tweetsData);
    
    if (tweetsData.data && tweetsData.data.length > 0) {
      console.log(`Found ${tweetsData.data.length} tweets for ${user}`);
      return tweetsData.data.map((tweet) => ({
        id: tweet.id,
        text: tweet.text,
        user: user,
      }));
    } else {
      console.warn(`No tweets found for ${user}`, tweetsData);
      return [];
    }
  } catch (error) {
    console.error(`Error fetching tweets for ${user}:`, error);
    return [];
  }
};

const updateTweets = async () => {
  // Check if we're currently rate limited
  const result = await new Promise((resolve) => {
    chrome.storage.local.get(['rateLimited', 'lastRateLimit'], resolve);
  });
  
  if (result.rateLimited && result.lastRateLimit) {
    const timeSinceRateLimit = Date.now() - result.lastRateLimit;
    const rateLimitResetTime = 15 * 60 * 1000; // 15 minutes in milliseconds
    
    if (timeSinceRateLimit < rateLimitResetTime) {
      console.log('Still rate limited, skipping update');
      return;
    } else {
      // Rate limit has expired, clear the flag
      chrome.storage.local.set({ rateLimited: false, lastRateLimit: null });
    }
  }
  
  // Proceed with update
  let allTweets = [];
  for (const user of users) {
    const tweets = await getTweets(user);
    allTweets = allTweets.concat(tweets);
  }
  // Store tweets in chronological order (newest first)
  allTweets.sort((a, b) => b.id - a.id);
  chrome.storage.local.set({ tweets: allTweets }, () => {
    console.log("Tweets updated and stored.");
  });
};

// Set up an alarm to update tweets every 30 minutes (reduced frequency to avoid rate limits)
chrome.alarms.create("twitterFeedUpdate", { periodInMinutes: 30 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "twitterFeedUpdate") {
    updateTweets();
  }
});

// Initial update when the extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  updateTweets();
});