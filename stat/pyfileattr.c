#include <Python.h>
#include <sys/stat.h>
#include <utime.h>
#include <time.h>
#include <errno.h>

static PyObject* get_file_times(PyObject* self, PyObject* args) {
    const char* path;
    struct stat fileStat;

    if (!PyArg_ParseTuple(args, "s", &path)) {
        return NULL; // Argument parsing failed
    }

    if (stat(path, &fileStat) < 0) {
        return PyErr_SetFromErrno(PyExc_OSError);
    }

    // Create a tuple to hold access time, modification time, and creation time
    return Py_BuildValue("kkk", fileStat.st_atime, fileStat.st_mtime, fileStat.st_ctime);
}

static PyObject* set_file_times(PyObject* self, PyObject* args) {
    const char* path;
    time_t access_time, modification_time;

    if (!PyArg_ParseTuple(args, "sKK", &path, &access_time, &modification_time)) {
        return NULL; // Argument parsing failed
    }

    struct utimbuf new_times;
    new_times.actime = access_time;       // Set access time
    new_times.modtime = modification_time; // Set modification time

    if (utime(path, &new_times) < 0) {
        return PyErr_SetFromErrno(PyExc_OSError);
    }

    Py_RETURN_NONE; // No error
}

static PyMethodDef FileAttrMethods[] = {
    {"get_file_times", get_file_times, METH_VARARGS, "Get access, modification, and creation times of a file."},
    {"set_file_times", set_file_times, METH_VARARGS, "Set access and modification times of a file."},
    {NULL, NULL, 0, NULL} // Sentinel
};

static struct PyModuleDef fileattrmodule = {
    PyModuleDef_HEAD_INIT,
    "pyfileattr", // name of module
    NULL, // module documentation, may be NULL
    -1, // size of per-interpreter state of the module, or -1 if the module keeps state in global variables
    FileAttrMethods
};

PyMODINIT_FUNC PyInit_pyfileattr(void) {
    return PyModule_Create(&fileattrmodule);
}
