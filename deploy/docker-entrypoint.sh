#!/bin/sh
set -eu

load_secret_file() {
    variable_name="$1"
    file_variable_name="${variable_name}_FILE"
    eval "file_path=\${${file_variable_name}:-}"
    eval "direct_value=\${${variable_name}:-}"

    if [ -n "$file_path" ] && [ -n "$direct_value" ]; then
        echo "Both $variable_name and $file_variable_name are set." >&2
        exit 1
    fi
    if [ -z "$file_path" ]; then
        return
    fi
    if [ ! -r "$file_path" ]; then
        echo "$file_variable_name does not point to a readable file." >&2
        exit 1
    fi

    secret_value="$(cat "$file_path")"
    if [ -z "$secret_value" ]; then
        echo "$file_variable_name points to an empty file." >&2
        exit 1
    fi
    export "$variable_name=$secret_value"
}

load_secret_file JYOTHISYAM_API_KEY
load_secret_file JYOTHISYAM_SUPABASE_SERVICE_ROLE_KEY

exec "$@"
