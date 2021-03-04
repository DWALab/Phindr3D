function flag=writestr(fname,data,wflag)

% function to write a matrix to a file
% usage flag=writedat(filename,data,write_flag)

n=size(data);
flag=1;
if n > 0

 if strcmpi(wflag,'Append'),
    fid=fopen(fname,'a');
 elseif strcmpi(wflag,'Overwrite'),
    fid=fopen(fname,'w');
 else
    if exist(fname,'file')~=0 
     return
    else
     fid=fopen(fname,'w');
    end
 end

 if fid==-1,
    str=sprintf('File %s cannot be opened. Check if it is opened in another program.',fname);
    warndlg(str,'File open error');
    flag=0;
    return
 end
 
 for i=1:n(1)   
  fprintf(fid,'%s',strtrim(sprintf('%s\t',data{i,:})));
  fprintf(fid,'\n');
 end

 fclose(fid);
end
return