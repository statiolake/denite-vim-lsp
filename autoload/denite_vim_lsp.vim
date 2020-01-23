let s:last_req_id = 0

function! s:not_supported(what) abort
    return lsp#utils#error(a:what.' not supported for '.&filetype)
endfunction

function! s:handle_symbol(server, last_req_id, type, data) abort
    if a:last_req_id != s:last_req_id
        return
    endif

    if lsp#client#is_error(a:data['response'])
        call lsp#utils#error('Failed to retrieve '. a:type . ' for ' . a:server . ': ' . lsp#client#error_message(a:data['response']))
        return
    endif

    let l:results = a:data['response']['result']
    let s:request_completed = v:true
    let s:results = l:results
endfunction

function! denite_vim_lsp#set_current_server() abort
    let s:servers = filter(lsp#get_whitelisted_servers(), 'lsp#capabilities#has_document_symbol_provider(v:val)')
endfunction

function! denite_vim_lsp#prepare_for_next_query() abort
    let s:results = []
    let s:last_req_id = (s:last_req_id + 1) % 100000
endfunction

function! denite_vim_lsp#request_completed() abort
    return s:request_completed
endfunction

function! denite_vim_lsp#try_get_results() abort
    if s:request_completed
        return s:results
    else
        return v:null
    endif
endfunction

function! denite_vim_lsp#document_symbol() abort
    let s:request_completed = v:false

    if len(s:servers) == 0
        call s:not_supported('Retrieving symbols')
        return
    endif

    for l:server in s:servers
        call lsp#send_request(l:server, {
            \ 'method': 'textDocument/documentSymbol',
            \ 'params': {
            \   'textDocument': lsp#get_text_document_identifier(),
            \ },
            \ 'sync': 1,
            \ 'on_notification': function('s:handle_symbol', [l:server, s:last_req_id, 'documentSymbol']),
            \ })
    endfor
endfunction

function! denite_vim_lsp#workspace_symbol(query) abort
    let s:request_completed = v:false

    if len(s:servers) == 0
        call s:not_supported('Retrieving workspace symbols')
        return
    endif

    for l:server in s:servers
        call lsp#send_request(l:server, {
            \ 'method': 'workspace/symbol',
            \ 'params': {
            \   'query': a:query,
            \ },
            \ 'sync': 1,
            \ 'on_notification': function('s:handle_symbol', [l:server, s:last_req_id, 'workspaceSymbol']),
            \ })
    endfor
endfunction
