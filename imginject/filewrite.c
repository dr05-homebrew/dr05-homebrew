#include <stdint.h>
#include <stdio.h>
#include "filewrite.h"


void write_to_file(char* filename, uint8_t* buffer, uint32_t offset, uint32_t width, uint32_t height)
{
	FILE* outfile = fopen(filename, "w+");
	fprintf(outfile, "P4\n%d %d\n", width, height);
	for ( uint32_t i = 0; i <= width*height/8; i++)
	{
		fputc(buffer[offset + i],outfile);
	}	
	fclose(outfile);
}

void dump_element(char* prefix, uint8_t* buffer, uint32_t offset, uint32_t count, uint32_t width, uint32_t height)
{
	char namebuf[1024];
	for ( int i = 0; i < count ; i++ )
	{
		sprintf(namebuf, "out/%s%d.pbm", prefix, i);
		write_to_file(namebuf, buffer, offset + (width/8*height*i), width, height);
	}
}