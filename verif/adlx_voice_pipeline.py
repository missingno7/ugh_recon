"""Replay accepted start/fade/stop corpus with the full seven-unit audio build."""
from adlx_voice_build import OUT,build
import adlx_music_corpus as corpus
corpus.OUT=OUT;corpus.build=build;corpus.contacts_reference.OUT=OUT/'reference'
if __name__=='__main__':corpus.main()
