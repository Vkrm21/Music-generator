@echo off
echo 🚀 Deploying ProMusicGen to Vercel...
echo.

echo 📦 Installing dependencies...
call npm install

echo.
echo 🔗 Logging into Vercel...
call vercel login

echo.
echo 📤 Deploying to Vercel with archive compression...
call vercel --prod --archive=tgz

echo.
echo ✅ Deployment complete!
echo Your ProMusicGen web app is now live on Vercel!
pause