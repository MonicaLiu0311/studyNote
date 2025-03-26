#pragma once

#include <iostream>

#ifdef EXPORT_TEST_DLL
    #ifdef BUILD_DLL
        #define FUNCTION_EXPORT __declspec(dllexport)
    #else
        #define FUNCTION_EXPORT __declspec(dllimport)
    #endif
#else
    #define FUNCTION_EXPORT
#endif

// TODO: Reference additional headers your program requires here.
FUNCTION_EXPORT int test();