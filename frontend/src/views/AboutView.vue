<template>
  <div class="about-page">

    <div class="about-hero">
      <h1 class="about-title">What does this do?</h1>
      <p class="about-lead">It studies 11 years of Premier League results and uses that history to work out the chances of any fixture ending as a home win, draw, or away win, before a ball is kicked.</p>
    </div>

    <div class="about-grid">
      <div class="about-card">
        <div class="about-card-icon">📊</div>
        <h3>It learned from history</h3>
        <p>The model was fed every Premier League match from 2015 to 2025, over 4,000 games. For each one it looked at recent form, goals scored, goals conceded, and the head-to-head record between the two clubs.</p>
      </div>
      <div class="about-card">
        <div class="about-card-icon">🔢</div>
        <h3>It found patterns</h3>
        <p>A gradient boosted classifier went through all of that history and learned which patterns, like a team on a five-game winning run at home, tend to lead to which results. It weights recent form more heavily than old results.</p>
      </div>
      <div class="about-card">
        <div class="about-card-icon">⚖️</div>
        <h3>It gives chances, not verdicts</h3>
        <p>Football is hard to call. Instead of saying "Arsenal will win", it says "58% Arsenal, 22% draw, 20% Chelsea." Three numbers that always add up to 100%. The spread tells you how open the game looks.</p>
      </div>
      <div class="about-card">
        <div class="about-card-icon">🔄</div>
        <h3>It stays current</h3>
        <p>Every Monday and Thursday it pulls the latest results, retrains on the new data, and updates itself. The form figures it uses always reflect what has happened recently, not a snapshot from months ago.</p>
      </div>
    </div>

    <div class="about-section">
      <h2 class="about-section-title">Reading a prediction</h2>
      <div class="about-explainer">
        <div class="about-explainer-row">
          <div class="about-explainer-label">Home Win 64%</div>
          <div class="about-explainer-desc">In fixtures that look like this one, based on form and history, the home side wins roughly two times out of three.</div>
        </div>
        <div class="about-explainer-row">
          <div class="about-explainer-label">Draw 21%</div>
          <div class="about-explainer-desc">About one in five similar games ends level. Draws get their own number rather than being split between the two win probabilities.</div>
        </div>
        <div class="about-explainer-row">
          <div class="about-explainer-label">Away Win 15%</div>
          <div class="about-explainer-desc">Away teams win less often on average, but this number moves up or down based on how both teams have been playing lately.</div>
        </div>
        <div class="about-explainer-row">
          <div class="about-explainer-label">Confidence 64%</div>
          <div class="about-explainer-desc">This is just the highest of the three numbers. Above 70% the model is fairly sure; below 45% it sees the game as wide open.</div>
        </div>
      </div>
    </div>

    <div class="about-section">
      <h2 class="about-section-title">What each tab does</h2>
      <div class="about-tabs-guide">
        <div class="about-tab-row">
          <span class="about-tab-name">Predict</span>
          <span class="about-tab-desc">Pick any two teams and get a live prediction with the three probabilities and recent form for both sides.</span>
        </div>
        <div class="about-tab-row">
          <span class="about-tab-name">Backtesting</span>
          <span class="about-tab-desc">See how the model performed on the 2025–26 season, games it had never seen. This is the real test of whether it holds up.</span>
        </div>
        <div class="about-tab-row">
          <span class="about-tab-name">Table</span>
          <span class="about-tab-desc">The actual Premier League standings for any season in the dataset, with European places colour coded.</span>
        </div>
        <div class="about-tab-row">
          <span class="about-tab-name">Teams</span>
          <span class="about-tab-desc">A full breakdown for any club: points per game, home and away record, goal difference, and their last five results.</span>
        </div>
        <div class="about-tab-row">
          <span class="about-tab-name">Pipeline</span>
          <span class="about-tab-desc">The technical side: how the model was built, which stats it leans on most, and how accurate it tested out.</span>
        </div>
      </div>
    </div>

  </div>
</template>
