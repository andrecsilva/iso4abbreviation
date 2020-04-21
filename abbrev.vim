" Vim plugin for abbreviating titles in ISO4 standard

let s:save_cpo = &cpo
set cpo&vim

if exists("g:loaded_iso4abbrev")
	finish
endif

let g:loaded_iso4abbrev = 1

if !hasmapto(':set operatorfunc=<SID>Abbreviate<cr>g@')
	nnoremap <unique> <leader>a :set operatorfunc=<SID>Abbreviate<cr>g@
	vnoremap <unique> <leader>a :<c-u>call <SID>Abbreviate(visualmode())<cr>
endif

function! s:Abbreviate(type)
	let saved = @@
	if a:type ==# 'v'
		execute "normal! `<v`>d"
	elseif a:type ==# 'char'
		execute "normal! `[v`]d"
	elseif a:type ==# 'V' 

	else
		return
	endif

	"TODO return @@ to original value
	let abbreviation = substitute(system("./abbr.py",@@), '\n', '', 'g')
	execute "normal! i\<C-r>\<C-r>=abbreviation\<CR>\<Esc>"
	let @@ = saved
endfunction

let &cpo = s:save_cpo
unlet s:save_cpo
