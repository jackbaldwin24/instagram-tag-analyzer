# Instagram Tag Contest Analyzer

## 📌 Overview
![Contest rules screenshot](post.png)

I entered an Instagram contest ([this post on Instagram](https://www.instagram.com/p/DRNG46vASoz/)) where the winner was supposed to get the **opening DJ slot for a show**.
The rules were simple on paper: people comment on the contest post and **tag their favorite local artist**, and the artist with the most tags wins.

I wanted a way to see how I was actually doing in the contest — not just by scrolling through comments, but by counting how many times each artist was tagged, and how many **unique people** tagged each artist.

---

## 🔍 What This Project Does

### ✔ Parse the copied comments from Instagram  
Comments are structured like:

```
username's profile picture
username
 <time since comment> (2d, 3h, 5m, etc.)
@artist1 @artist2
```

The script reads this format and extracts:
- the commenter’s username  
- the tags inside each comment

---

## 🏆 Two Types of Leaderboards

### **1. Raw Tag Count (WITH duplicates)**  
Counts *every* time an `@tag` appears.

Example:
- If someone tags `@dj_example` 10 times → counts as 10  
- If a person spams the same artist → all counted  
- This shows total hype + spam + activity

This is how Instagram **looks** when scrolling the comments.

---

### **2. Unique Voter Count (WITHOUT duplicates)**  
Counts **unique commenters** per artist.

Example:
- If someone tags `@basslord9000` 20 times → counts as **1 vote**
- If someone tags `@basslord9000` again in a different comment → still **1 vote**
- Shows REAL support, not spam

This is the **fairest measure** of who the crowd actually supports.

---

## 📁 Files

- `comments.txt` — raw IG comments (copied & pasted from the post)
- `analyze.py` — main script to parse and analyze
- `README.md` — this file

---

## ▶️ How to Run

1. On desktop, open the Instagram contest post.
2. Scroll through the comments **all the way to the bottom** so every comment loads.
3. Press **Ctrl + A** (Windows) or **Cmd + A** (Mac) to select the entire page.
4. Copy and paste everything into `comments.txt` (overwrite any previous content).
5. Run:

```
python3 analyze.py
```

3. The script will print:
- Top 10 artists by **total tag mentions** (with duplicates)
- Top 10 artists by **unique voters** (no duplicates)

---

## 🎯 Why I Built This

I wanted to understand:
- how many total tags each artist received,
- how many **unique people** tagged each artist,
- and where I stood in the contest compared to other artists.

Instagram only shows the mess — this script finds the truth underneath it.

**Edit:** The original Instagram contest post has since been deleted. The `comments.txt` snapshot in this repo was last updated around **7:30 PM on 11/20**, roughly **45 minutes before** the winner was announced.
