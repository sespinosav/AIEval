// Add any JavaScript functionality you want for the main page here.
// For example, you could add event listeners to the links
// to track which functionality is being accessed.

document.addEventListener('DOMContentLoaded', () => {
    const frontendLinks = document.querySelectorAll('.frontend-link');
  
    frontendLinks.forEach(link => {
      link.addEventListener('click', (event) => {
        // Example: Log which functionality was clicked
        console.log(`Navigating to: ${event.target.textContent}`);
      });
    });
  });