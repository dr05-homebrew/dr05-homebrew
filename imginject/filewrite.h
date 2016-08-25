#pragma once
void write_to_file(char* filename, uint8_t* buffer, uint32_t offset, uint32_t width, uint32_t height);
void dump_element(char* prefix, uint8_t* buffer, uint32_t offset, uint32_t count, uint32_t width, uint32_t height);