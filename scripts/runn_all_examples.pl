#!/bin/perl -w

foreach $file (<data/examples/*.yaml>) {
  unless($file=~/.*\.completed\.yaml$/){
    print "$file\n";
    print `toskerise $file`."\n";
  }
}
