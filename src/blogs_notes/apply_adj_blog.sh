#!/bin/bash

# Check if folder argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <folder-path>"
  echo "Example: $0 dist"
  exit 1
fi

FOLDER="$1"

# Check if folder exists
if [ ! -d "$FOLDER" ]; then
  echo "Error: Folder '$FOLDER' does not exist"
  exit 1
fi

echo "Adding margins to HTML files in $FOLDER..."

for f in "$FOLDER"/index.html "$FOLDER"/*/index.html; do
  if [ -f "$f" ]; then
    perl -i -pe '
      if (m|</head>|) {
        $_ = q|<style>
/* ── Layout & scroll fix ── */
html, body {
  overflow: auto !important;
  height: auto !important;
}
.notion-app,
.notion-frame,
.notion-scroller {
  overflow: visible !important;
  height: auto !important;
  min-height: unset !important;
}

/* ── Hide topbar ── */
.notion-topbar { display: none !important; }

/* ── Side margins ── */
.notion-frame {
  padding-left: 96px !important;
  padding-right: 96px !important;
}

/* ── Content width & zoom ── */
.notion-page-content {
  max-width: 900px !important;
  margin-left: auto !important;
  margin-right: auto !important;
  zoom: 1.25;
}

/* ── Mobile ── */
@media (max-width: 768px) {
  .notion-frame {
    padding-left: 24px !important;
    padding-right: 24px !important;
  }
  .notion-page-content {
    zoom: 1;
  }
}
</style>| . $_;
      }
    ' "$f"
    echo "Processed: $f"
  fi
done

echo "Done!"