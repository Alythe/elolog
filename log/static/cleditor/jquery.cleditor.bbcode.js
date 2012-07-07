/**
 @preserve CLEditor BBCode Plugin v1.0.0
 http://premiumsoftware.net/cleditor
 requires CLEditor v1.3.0 or later
 
 Copyright 2010, Chris Landowski, Premium Software, LLC
 Dual licensed under the MIT or GPL Version 2 licenses.
*/

// ==ClosureCompiler==
// @compilation_level SIMPLE_OPTIMIZATIONS
// @output_file_name jquery.cleditor.bbcode.min.js
// ==/ClosureCompiler==

/*

  The CLEditor useCSS optional parameter should be set to false for this plugin
  to function properly.

  Supported HTML and BBCode Tags:

  Bold              <b>Hello</b>
                    [b]Hello[/b]
  Italics           <i>Hello</i>
                    [i]Hello[/i]
  Underlined        <u>Hello</u>
                    [u]Hello[/u]
  Strikethrough     <strike>Hello</strike>
                    [s]Hello[/s]
  Unordered Lists   <ul><li>Red</li><li>Blue</li><li>Green</li></ul>
                    [list][*]Red[/*][*]Green[/*][*]Blue[/*][/list]
  Ordered Lists     <ol><li>Red</li><li>Blue</li><li>Green</li></ol>
                    [list=1][*]Red[/*][*]Green[/*][*]Blue[/*][/list]
  Images            <img src="http://premiumsoftware.net/image.jpg">
                    [img]http://premiumsoftware.net/image.jpg[/img]
  Links             <a href="http://premiumsoftware.net">Premium Software</a>
                    [url=http://premiumsoftware.net]Premium Software[/url]

*/

(function($) {

  // BBCode only supports a small subset of HTML, so remove
  // any toolbar buttons that are not currently supported.
  $.cleditor.defaultOptions.controls =
    "bold italic underline strikethrough removeformat | bullets numbering | " +
    "undo redo | image link unlink | cut copy paste pastetext | print source";

  // Save the previously assigned callback handlers
  var oldAreaCallback = $.cleditor.defaultOptions.updateTextArea;
  var oldFrameCallback = $.cleditor.defaultOptions.updateFrame;

  // Wireup the updateTextArea callback handler
  $.cleditor.defaultOptions.updateTextArea = function(html) {

    // Fire the previously assigned callback handler
    if (oldAreaCallback)
      html = oldAreaCallback(html);

    // Convert the HTML to BBCode
    return $.cleditor.convertHTMLtoBBCode(html);

  }

  // Wireup the updateFrame callback handler
  $.cleditor.defaultOptions.updateFrame = function(code) {

    // Fire the previously assigned callback handler
    if (oldFrameCallback)
      code = oldFrameCallback(code);

    // Convert the BBCode to HTML
    return $.cleditor.convertBBCodeToHTML(code);

  }

  // Expose the convertHTMLtoBBCode method
  $.cleditor.convertHTMLtoBBCode = function(html) {
		
    $.each([
      [/[\r|\n]/g, ""],
      [/<br.*?>/gi, "\n"],
      [/<b>([\s\S]*?)<\/b>/gi, "[b]$1[/b]"],
      [/<strong>([\s\S]*?)<\/strong>/gi, "[b]$1[/b]"],
      [/<i>([\s\S]*?)<\/i>/gi, "[i]$1[/i]"],
      [/<em>([\s\S]*?)<\/em>/gi, "[i]$1[/i]"],
      [/<u>([\s\S]*?)<\/u>/gi, "[u]$1[/u]"],
      [/<ins>([\s\S]*?)<\/ins>/gi, "[u]$1[/u]"],
      [/<strike>([\s\S]*?)<\/strike>/gi, "[s]$1[/s]"],
      [/<del>([\s\S]*?)<\/del>/gi, "[s]$1[/s]"],
      [/<a.*?href="([\s\S]*?)".*?>([\s\S]*?)<\/a>/gi, "[url=$1]$2[/url]"],
      [/<img.*?src="([\s\S]*?)".*?>/gi, "[img]$1[/img]"],
      [/<ul>/gi, "[list]"],
      [/<\/ul>/gi, "[/list]"],
      [/<ol>/gi, "[list=1]"],
      [/<\/ol>/gi, "[/list]"],
      [/<li>/gi, "[*]"],
      [/<\/li>/gi, "[/*]"],
      [/<.*?>([\s\S]*?)<\/.*?>/g, "$1"]
      ], function(index, item) {
        html = html.replace(item[0], item[1]);
      });

    return html;

  }

  // Expose the convertBBCodeToHTML method
  $.cleditor.convertBBCodeToHTML = function(code) {

    $.each([
      [/\r/g, ""],
      [/\n/g, "<br/>"],
      [/\[b\]([\s\S]*?)\[\/b\]/gi, "<b>$1</b>"],
      [/\[i\]([\s\S]*?)\[\/i\]/gi, "<i>$1</i>"],
      [/\[u\]([\s\S]*?)\[\/u\]/gi, "<u>$1</u>"],
      [/\[s\]([\s\S]*?)\[\/s\]/gi, "<strike>$1</strike>"],
      [/\[url=([\s\S]*?)\]([\s\S]*?)\[\/url\]/gi, "<a href=\"$1\">$2</a>"],
      [/\[img\]([\s\S]*?)\[\/img\]/gi, "<img src=\"$1\">"],
      [/\[list\]([\s\S]*?)\[\/list\]/gi, "<ul>$1</ul>"],
      [/\[list=1\]([\s\S]*?)\[\/list\]/gi, "<ol>$1</ol>"],
      [/\[list\]/gi, "<ul>"],
      [/\[list=1\]/gi, "<ol>"],
      [/\[\*\]([\s\S]*?)\[\/\*\]/g, "<li>$1</li>"],
      [/\[\*\]/g, "<li>"]
      ], function(index, item) {
        code = code.replace(item[0], item[1]);
      });

    return code;

  }

})(jQuery);
