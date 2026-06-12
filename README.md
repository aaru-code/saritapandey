# Sarita Pandey — Static Site

This workspace contains a static site for LIC agent Sarita Pandey.

Quick tasks performed:
- Updated "Explore" and "Enquire Now" buttons to open LIC homepage: https://licindia.in/hi/web/guest/home
- Updated branch/address to: Sathiaon, Azamgarh, Uttar Pradesh 276406

How to push to GitHub and deploy to Vercel

1. Initialize git, commit, and push to a GitHub repo (replace `<your-repo-url>`):

```bash
git init
git add .
git commit -m "Site: update LIC links and address"
git remote add origin <your-repo-url>
git push -u origin main
```

2. Deploy to Vercel (recommended):

```bash
# install Vercel CLI
npm i -g vercel
# login and deploy
vercel login
vercel --prod
```

Vercel will detect this as a static site and serve from the project root.

Notes
- If you want me to create a GitHub repo and push for you, I need a remote URL and permission (or you can run the above locally).
- I made the buttons open the LIC Hindi homepage in a new tab for user safety (`target="_blank" rel="noopener"`).

Next steps I can take for you:
- Run a responsive audit and apply CSS fixes across components.
- Create a GitHub repo and push changes (you'll need to provide credentials or run the push locally).
- Connect Vercel via the web dashboard or CLI and complete the deployment.
