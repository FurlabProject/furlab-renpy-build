#ifndef RENPY_EMBED_H
#define RENPY_EMBED_H

#ifdef __cplusplus
extern "C"
{
#endif

  int renpy_embed_init(int argc, char **argv);
  int renpy_run_game(
      const char *renpy_base_path,
      const char *game_root_path,
      const char *save_root_path);
  int renpy_request_quit(void);

#ifdef __cplusplus
}
#endif

#endif