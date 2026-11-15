#include "session_world.h"
#include <stdlib.h>
static NativeSessionWorld world;
NativeSessionWorld *native_session_world(void){return &world;}
int session_world_run(const SessionServices *services,void *context){
 SessionObserver observe=services->observe;SessionExecutor execute=services->execute;
 SessionDiagnostic diagnostic=services->diagnostic;
 SessionProcess process;session_begin(&process);
 for(;;){
  SessionRequest request=session_next(&process,observe(context,process.phase));
  if(request.action==SESSION_INVALID)abort();
  if(request.action==SESSION_FINISHED){if(!session_complete(&process))abort();return 0;}
  int status=execute(context,request);
  if(status)return status;
  if(!session_acknowledge(&process,request.action,observe(context,process.phase)))abort();
  if(diagnostic){status=diagnostic(context,&process);if(status)return status;}
 }
}
