from django import template

register = template.Library()

def paginator(context, adjacent_pages=2):
	"""
	To be used in conjunction with the object_list generic view.

	Adds pagination context variables for use in displaying first, adjacent and
	last page links in addition to those created by the object_list generic
	view.

	"""
	page = context['machinelists'].number
	pages = context['machinelists'].paginator.num_pages
	paginator = context['machinelists'].paginator
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
		'results_per_page': context['machinelists'].paginator.per_page,
		'page': page,
		'pages': pages,
		'page_numbers': page_numbers,
		'next': context['machinelists'].next_page_number(),
		'previous': context['machinelists'].previous_page_number(),
		'has_next': context['machinelists'].has_next(),
		'has_previous': context['machinelists'].has_previous(),
		'show_first': 1 not in page_numbers,
		'show_last': pages not in page_numbers,
		'total_records':context['machinelists'].paginator.count
	}

register.inclusion_tag('qmul_paginator.html', takes_context=True)(paginator)

