# Pandoc Publisher

Pandoc MD to HTML with some good but hacky defaults

Uses `_pre` and `_post` HTML templates to:

* Add Water.css styling to the text
* Use Prism.js for syntax highlighting

Uses a lua filter to 

* Fix a bug where `<pre>` and `<code>` appear in the wrong order, breaking syntax highlighting

Additionally

* Generate a title and meta description from the markdown and add to the HTML

Includes a basic form for the user to upload a markdown file and get the HTML back, but intended to be used from CURL or similar.
