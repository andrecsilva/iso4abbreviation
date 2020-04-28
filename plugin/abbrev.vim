" Vim plugin for abbreviating titles in ISO4 standard
" Maintainer: André C. Silva <andre.ufs@gmail.com>
let s:save_cpo = &cpo
set cpo&vim

if exists("g:loaded_iso4abbrev")
	finish
endif

let s:path = expand('<sfile>:p:h' . '../python3')

py3 import vim
py3 import os
py3 from abbr import Trie
py3 import abbr
"Building the Tries are quite expensive, thus they are cached
py3 abbr_prefixTrie, abbr_suffixTrie, abbr_lastWordTrie = abbr.getTries(vim.eval('s:path'))

"let g:loaded_iso4abbrev = 1

if !hasmapto(':set operatorfunc=<SID>Abbreviate<cr>g@')
	nnoremap <unique> <leader>a :set operatorfunc=<SID>Abbreviate<cr>g@
	vnoremap <unique> <leader>a :<c-u>call <SID>Abbreviate(visualmode())<cr>
endif

function! s:Abbreviate(type)
	if a:type ==# 'v'  || a:type ==# 'char'
		let saved = @@
		"TODO make 'v' respect linebreaks
		if a:type ==# 'v'
			execute "normal! `<v`>d"
		elseif a:type ==# 'char'
			execute "normal! `[v`]d"
		endif

		py3 string_to_abbreviate = vim.eval("@@")
		py3 vim.command('let l:abbreviation="{}"'.format(
		\ abbr.cleanAndAbbreviate(vim.eval('@@'),abbr_prefixTrie,abbr_suffixTrie,abbr_lastWordTrie)))

		execute "normal! i\<C-r>\<C-r>=l:abbreviation\<CR>\<Esc>"

		let @@ = saved

	elseif a:type ==# 'V'
		'<,'>py3do return abbr.cleanAndAbbreviate(line,abbr_prefixTrie,abbr_suffixTrie,abbr_lastWordTrie)
	else
		return
	endif


endfunction

let &cpo = s:save_cpo
unlet s:save_cpo
