#/usr/bin/env bash
_linuxmuster-linuxclient7_completions()
{
  if [ "${#COMP_WORDS[@]}" != "2" ]; then
    return
  fi

  COMPREPLY=($(compgen -W "setup prepare-image print-logs status" "${COMP_WORDS[1]}"))
}

complete -F _linuxmuster-linuxclient7_completions linuxmuster-linuxclient7