project(
  'budgie-analog-clock',
  version: '0.0.1-dev',
  license: 'GPL3+',
  meson_version: '>= 0.40.0'
)


application_id = 'budgie-analog-clock'

prefix = get_option('prefix')
libdir = join_paths(prefix, get_option('libdir'))

subdir('src')

install_data('schema/com.github.samlane-ma.budgie-analog-clock.gschema.xml',
    install_dir: '/usr/share/glib-2.0/schemas'
)

meson.add_install_script('meson_post_install')
