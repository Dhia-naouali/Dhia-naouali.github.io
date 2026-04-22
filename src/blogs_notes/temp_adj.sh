#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <folder-path>"
  echo "Example: $0 dist"
  exit 1
fi

FOLDER="$1"

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
/* Break the viewport-height lock */
html, body {
  height: auto !important;
  overflow: auto !important;
}
.notion-app-inner,
.notion-app-inner > div {
  height: auto !important;
  min-height: 100vh !important;
}
.notion-cursor-listener {
  height: auto !important;
  min-height: 100vh !important;
}
/* Main culprit: notion-frame has inline height: calc(-44px + 100vh) */
.notion-frame {
  height: auto !important;
  max-height: none !important;
  overflow: visible !important;
  padding-left: 96px !important;
  padding-right: 96px !important;
}
.notion-scroller {
  overflow: visible !important;
  height: auto !important;
}
/* Hide topbar */
.notion-topbar { display: none !important; }
/* Content width and zoom */
.notion-page-content {
  max-width: 900px !important;
  margin-left: auto !important;
  margin-right: auto !important;
  zoom: 1.25;
}
@media (max-width: 768px) {
  .notion-frame {
    padding-left: 24px !important;
    padding-right: 24px !important;
  }
  .notion-page-content { zoom: 1; }
}
</style>| . $_;
      }
    ' "$f"
    echo "Processed: $f"
  fi
done

echo "Done!"
