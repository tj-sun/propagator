/*  Copyright (C) 2015 Imperial College London and others.
 *
 *  Please see the AUTHORS file in the main source directory for a
 *  full list of copyright holders.
 *
 *  Gerard Gorman
 *  Department of Earth Science and Engineering
 *  Imperial College London
 *
 *  g.gorman@imperial.ac.uk
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *  1. Redistributions of source code must retain the above copyright
 *  notice, this list of conditions and the following disclaimer.
 *  2. Redistributions in binary form must reproduce the above
 *  copyright notice, this list of conditions and the following
 *  disclaimer in the documentation and/or other materials provided
 *  with the distribution.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 *  CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 *  INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 *  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 *  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
 *  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 *  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
 *  TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 *  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 *  ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
 *  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
 *  THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 *  SUCH DAMAGE.
 */

#include <iostream>
#include <algorithm>

#include "opesciIO.h"
#include "opesciHandy.h"

int main(int argc, char *argv[]){  
  std::string filename(argv[1]);

  std::string basename;
  {
    size_t pos = filename.rfind(".sgy");
    if(pos==std::string::npos){
      pos = filename.rfind(".segy");
    }
    if(pos==std::string::npos){
      pos = filename.rfind(".SGY");
    }
    if(pos==std::string::npos){
      pos = filename.rfind(".SEGY");
    }
    if(pos==std::string::npos){
      opesci_abort("Do not recognise file extension. Expecting either .segy or .sgy");
    }
    basename = filename.substr(0, pos);
  }

  std::vector<float> array;
  int dim[] = {1, 1, 1};
  float spacing[] = {1.0, 1.0, 1.0};
  
  opesci_read_model_segy(filename.c_str(), array, dim, spacing);
  opesci_dump_field_vts(basename, dim, spacing, array);

  return 0;
}
