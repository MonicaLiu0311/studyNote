linux ���ٸ���vcpkg ʹ�õĽű����ܹ�����ǳ��򵥵�port���������°汾�� sha512, ����version,����pr��

ʹ�����ӣ�

update-vcpkg-port 

����portfile��REF�ֶΰ���${VERSION}�����}

./update-vcpkg-port fruit 3.7.1 version v createbranch 
fruit��port���� 
3.7.1���°汾�ţ�version��portfile��REF�ֶθ�дΪ����"${VERSION}"��
v ��${VERSION}�滻Ϊv${VERSION}
createbranch�Ǵ�����֧

����ʱ����
  ���ش���fruit��֧���޸�vcpkg.json�е�versionΪ�°汾����3.7.1
  ����һ��vcpkg install��ȡActual hashһ���޸�portfile
  ������һ��vcpkg installȷ������ͨ��
  ����ɹ�
    �ύ�޸�
    ����pr��
https://github.com/microsoft/vcpkg/pull/34182 ��һ������������

����portfile��REF�ֶβ�����${VERSION}�����}
����portfile��
REF�ֶε�ֵ���滻Ϊ���ĸ��������ı����������滻Ϊ�°汾git-sha 9b4a163a9a97c900b0febd93e22dc1be3faf6e20   
./update-vcpkg-port LukasBanana/GaussianLib 2023-02-17 ref 9b4a163a9a97c900b0febd93e22dc1be3faf6e20  createbranch  
https://github.com/microsoft/vcpkg/pull/34154 


ʹ��ǰ��Ҫ��װgh ripgrep fd����Щ������linux����brew������װ��




