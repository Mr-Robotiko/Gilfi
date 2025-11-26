# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "Debug")
  file(REMOVE_RECURSE
  "CMakeFiles\\Gilfi_autogen.dir\\AutogenUsed.txt"
  "CMakeFiles\\Gilfi_autogen.dir\\ParseCache.txt"
  "Gilfi_autogen"
  )
endif()
