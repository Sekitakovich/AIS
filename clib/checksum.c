// gcc -shared -fPIC checksum.c -o libCheckSum.so

int checksum(unsigned char *p, int length){
  int value = 0;
  while(length--){
    value ^= (*p++);
  }
  return(value);
}
