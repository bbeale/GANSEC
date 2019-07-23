import os
import random

"""
	naked_tags and events contain HTML tags and DOM events, but they could be anything. Whatever components make up 
	the attack strings you are trying to create should go here.
"""
naked_tags = [
	"<",
	">",
	"/>",
	"\"<",
	"\">",
	"\"/>",
	"<\"",
	">\"",
	"/>\"",
	"'<",
	"'>",
	"'/>",
	"<'",
	">'",
	"/>'",
	"\"",
	"'",
	"a",
	"abbr",
	"address",
	"area",
	"article",
	"aside",
	"audio",
	"b",
	"base",
	"bdi",
	"bdo",
	"blockquote",
	"body",
	"br",
	"button",
	"canvas",
	"caption",
	"cite",
	"code",
	"col",
	"colgroup",
	"data",
	"datalist",
	"dd",
	"del",
	"details",
	"dfn",
	"dialog",
	"div",
	"dl",
	"dt",
	"em",
	"embed",
	"fieldset",
	"figcaption",
	"figure",
	"footer",
	"form",
	"h1",
	"h2",
	"h3",
	"h4",
	"h5",
	"h6",
	"head",
	"header",
	"hgroup",
	"hr",
	"html",
	"i",
	"iframe",
	"img",
	"input",
	"ins",
	"kbd",
	"keygen",
	"label",
	"legend",
	"li",
	"link",
	"main",
	"map",
	"mark",
	"math",
	"menu",
	"menuitem",
	"meta",
	"meter",
	"nav",
	"noscript",
	"object",
	"ol",
	"optgroup",
	"option",
	"output",
	"p",
	"param",
	"picture",
	"pre",
	"progress",
	"q",
	"rb",
	"rp",
	"rt",
	"rtc",
	"ruby",
	"s",
	"samp",
	"script",
	"section",
	"select",
	"slot",
	"small",
	"source",
	"span",
	"strong",
	"style",
	"sub",
	"summary",
	"sup",
	"svg",
	"table",
	"tbody",
	"td",
	"template",
	"textarea",
	"tfoot",
	"th",
	"thead",
	"time",
	"title",
	"tr",
	"track",
	"u",
	"ul",
	"var",
	"video",
	"wbr"
]

events = [
	"onafterprint",
	"onbeforeprint",
	"onbeforeonload",
	"onerror",
	"onhaschange",
	"onload",
	"onmessage",
	"onoffline",
	"ononline",
	"onpagehide",
	"onpageshow",
	"onpopstate",
	"onredo",
	"onresize",
	"onstorage",
	"onundo",
	"onunload",
	"href",
	"src",
	"onblur",
	"onchange",
	"oncontextmenu",
	"onfocus",
	"onformchange",
	"onforminput",
	"oninput",
	"oninvalid",
	"onreset",
	"onselect",
	"onsubmit",
	"onkeydown",
	"onkeypress",
	"onkeyup",
	"onclick",
	"ondblclick",
	"ondrag",
	"ondragend",
	"ondragenter",
	"ondragleave",
	"ondragover",
	"ondragstart",
	"ondrop",
	"onmousedown",
	"onmousemove",
	"onmouseout",
	"onmouseover",
	"onmouseup",
	"onmousewheel",
	"onscroll",
	"onabort",
	"oncanplay",
	"oncanplaythrough",
	"ondurationchange",
	"onemptied",
	"onended",
	"onerror",
	"onloadeddata",
	"onloadedmetadata",
	"onloadstart",
	"onpause",
	"onplay",
	"onplaying",
	"onprogress",
	"onratechange",
	"onreadystatechange",
	"onseeked",
	"onseeking",
	"onstalled",
	"onsuspend",
	"ontimeupdate",
	"onvolumechange",
	"onwaiting"
]

components = []
for tag in naked_tags:
	# Experimented with formatting the tags
	# ctag = tag
	# _tag = "<{}>".format(tag)
	# _ctag = "</{}>".format(ctag)

	# components.append(_tag)
	# components.append(_ctag)
	components.append(tag)

for event in events: 
	# components.append(event)
	pair = "{}=\"javascript:alert(1)\"".format(event)
	components.append(pair)


path_string = "gene/{}"

path = os.path.join(os.path.realpath(path_string.format("gene_list.csv")))

if not os.path.exists(path):
	raise FileNotFoundError("Path not found")

tag_list = []

with open(path, "w+") as pf:
	try:
		tag_list = pf.readlines()
	except IOError:
		print("fail")
	for new_tag in components:
		if new_tag not in tag_list:
			tag_list.append(new_tag)

	for tag in tag_list:
		pf.write("{}\n".format(tag))

print("Done!")
