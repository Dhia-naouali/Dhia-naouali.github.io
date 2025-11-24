
# python loconotion   --chromedriver /usr/bin/chromedriver notion-link

for f in */index.html; do
  perl -i -pe '
    if (m|</head>|) {
      $_ = q|<style>
.notion-topbar { display: none !important; }
.notion-frame { padding-left: 3rem !important; }
</style>| . $_;
    }
  ' "$f"
done
