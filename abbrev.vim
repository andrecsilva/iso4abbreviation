nnoremap <leader>g :set operatorfunc=<SID>Abbreviate<cr>g@
vnoremap <leader>g :<c-u>call <SID>Abbreviate(visualmode())<cr>

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
