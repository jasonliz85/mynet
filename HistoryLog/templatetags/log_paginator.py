from django import template

register = template.Library()

def log_paginator(context, adjacent_pages=2):
	"""
	To be used in conjunction with the object_list generic view.

	Adds pagination context variables for use in displaying first, adjacent and
	last page links in addition to those created by the object_list generic
	view.

	"""
	page = context['historyLogs'].number
	pages = context['historyLogs'].paginator.num_pages
	paginator = context['historyLogs'].paginator
	startPage = max(page - adjacent_pages, 1)
	if startPage <= 3: 
		startPage = 1
	endPage = page + adjacent_pages + 1
	if endPage >= pages - 1: 
		endPage = pages + 1
	page_numbers = [n for n in range(startPage, endPage) \
		    if n > 0 and n <= pages]
	return {
		#'page_obj': page_obj,
		#'hits': context['hits'],
		'sort_type': context['sort']['type_bef'],
		'sort_order': context['sort']['order'],
		'list_len': context['list_size'],
		'paginator': paginator,
		'results_per_page': context['historyLogs'].paginator.per_page,
		'page': page,
		'pages': pages,
		'page_numbers': page_numbers,
		'next': context['historyLogs'].next_page_number(),
		'previous': context['historyLogs'].previous_page_number(),
		'has_next': context['historyLogs'].has_next(),
		'has_previous': context['historyLogs'].has_previous(),
		'show_first': 1 not in page_numbers,
		'show_last': pages not in page_numbers,
		'total_records':context['historyLogs'].paginator.count
	}

register.inclusion_tag('qmul_paginator.html', takes_context=True)(log_paginator)

