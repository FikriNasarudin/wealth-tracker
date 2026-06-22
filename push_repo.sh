#!/bin/bash
cd ~/projects/lab/wealth-tracker
git reset
git config user.email "fikrimuhamad900@gmail.com"
git config user.name "Fikri Nasarudin"
git branch -M main
git add .
git commit -m "Initial commit"
git push -u origin main
