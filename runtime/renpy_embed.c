#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "Python.h"
#include "renpy_embed.h"

#define EXPORT

int EXPORT renpy_run_game(const char *renpy_base_path,
                          const char *game_root_path,
                          const char *save_root_path)
{
  if (!Py_IsInitialized())
    return -1;

  PyGILState_STATE g = PyGILState_Ensure();

  // Ensure runtime path is in sys.path
  PyObject *sysmod = PyImport_ImportModule("sys");
  if (!sysmod)
  {
    PyErr_Print();
    PyGILState_Release(g);
    return -2;
  }

  PyObject *path = PyObject_GetAttrString(sysmod, "path");
  Py_DECREF(sysmod);
  if (!path)
  {
    PyErr_Print();
    PyGILState_Release(g);
    return -3;
  }

  PyObject *base = PyUnicode_FromString(renpy_base_path);
  if (!base)
  {
    PyErr_Print();
    Py_DECREF(path);
    PyGILState_Release(g);
    return -4;
  }

  int contains = PySequence_Contains(path, base);
  if (contains == 0)
  {
    PyList_Insert(path, 0, base);
  }
  else if (contains < 0)
  {
    PyErr_Print(); // sequence contains error
  }

  Py_DECREF(base);
  Py_DECREF(path);

  char code[8192];
  snprintf(code, sizeof(code),
           "import sys\n"
           "sys.modules.pop('FurlabRun', None)\n"
           "import FurlabRun\n"
           "FurlabRun.start(r'''%s''', r'''%s''', r'''%s''')\n",
           renpy_base_path, game_root_path, save_root_path);

  int rc = PyRun_SimpleString(code);

  if (rc != 0)
  {
    if (PyErr_ExceptionMatches(PyExc_SystemExit))
    {
      PyErr_Clear();
      PyGILState_Release(g);
      return 0;
    }
    PyErr_Print();
    PyGILState_Release(g);
    return -5;
  }

  PyGILState_Release(g);
  return 0;
}

int EXPORT renpy_request_quit(void)
{
  if (!Py_IsInitialized())
    return -1;

  PyGILState_STATE g = PyGILState_Ensure();

  int rc = PyRun_SimpleString(
      "import renpy\n"
      "renpy.pygame.event.post(renpy.pygame.event.Event(renpy.pygame.QUIT))\n");

  if (rc != 0)
    PyErr_Print();

  PyGILState_Release(g);
  return rc == 0 ? 0 : -2;
}