from ..views import *


class AddressApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if 'house_no' in request.data and 'area_street' in request.data and 'locality' in request.data:
                return self.create_address(request)
            
            elif 'set_default' in request.data and 'address_id' in request.data:
                return self.set_default_address(request)

            else:
                return Response({'status': 'fail', 'message': f'{BAD_REQUEST} - Invalid Request Parameters'}, 
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create_address(self, request):
        try:
            house_no = request.data.get("house_no")
            area_street = request.data.get("area_street")
            locality = request.data.get("locality")
            city = request.data.get("city")
            state = request.data.get("state")
            pincode = request.data.get("pincode")
            country = request.data.get("country", "India")
            contact_name = request.data.get("contact_name")
            contact_no = request.data.get("contact_no")
            address_type = request.data.get("address_type", "HOME")

            required = ['house_no', 'area_street', 'locality','city','state', 'pincode','contact_name', 'contact_no']
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing

            int_error = integer_field_validator(request, ['contact_no', 'pincode'])
            if int_error:
                return int_error

            address_count = Address.objects.filter(user=request.user,is_deleted=False).count()
            is_default = request.data.get("is_default", address_count == 0)

            with transaction.atomic():
                address = Address.objects.create(
                    user=request.user,
                    house_no=house_no,
                    area_street=area_street,
                    locality=locality,
                    city=city,
                    state=state,
                    pincode=pincode,
                    country=country,
                    contact_name=contact_name,
                    contact_no=contact_no,
                    address_type=address_type,
                    is_default=is_default,
                    created_by=request.user
                )

                if is_default:
                    Address.objects.filter(user=request.user,is_deleted=False).exclude(id=address.id).update(is_default=False)

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Address Created Successfully",
                "data": {
                    "address_id": address.id,
                    "house_no": address.house_no,
                    "area_street": address.area_street,
                    "locality": address.locality,
                    "city": address.city,
                    "state": address.state,
                    "pincode": address.pincode,
                    "country": address.country,
                    "contact_name": address.contact_name,
                    "contact_no": address.contact_no,
                    "address_type": address.address_type,
                    "is_default": address.is_default,
                    "full_address": f"{address.house_no}, {address.area_street}, {address.locality}, {address.city}, {address.state} - {address.pincode}"
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error - {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request):
        try:
            queryset = Address.objects.filter(user=request.user,is_deleted=False).order_by('-id')
            serializer = AddressSerializer(queryset, many=True)
            for item in serializer.data:
                item.pop('created_by', None)
                item.pop('updated_by', None)
                item.pop('is_deleted', None)
                item.pop('is_default', None)
                item.pop('created_at', None)
                item.pop('updated_at', None)

            response_data = {
                "status": "success",
                "message": "Address fetched successfully",
                "data": serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            address_id = request.query_params.get("address_id")
            house_no = request.data.get("house_no")
            area_street = request.data.get("area_street")
            locality = request.data.get("locality")
            city = request.data.get("city")
            state = request.data.get("state")
            pincode = request.data.get("pincode")
            country = request.data.get("country")
            contact_name = request.data.get("contact_name")
            contact_no = request.data.get("contact_no")
            address_type = request.data.get("address_type")
            is_default = request.data.get("is_default")

            missing = check_missing_fields(request.query_params, ['address_id'])
            if missing:
                return missing

            int_error = integer_field_validator(request, ['address_id'], source="params")
            if int_error:
                return int_error

            address = Address.objects.get(id=address_id, is_deleted=False)

            if address.user != request.user:
                return Response({"status": "fail", "message": f"{UNAUTHORIZED} - Unauthorized access"},
                                status=status.HTTP_403_FORBIDDEN)

            if not any([house_no, area_street, locality,city, state, pincode,contact_name, 
                        contact_no,address_type, country, is_default]):
                
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Please provide at least one field to update"},
                                status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                if house_no:
                    address.house_no = house_no

                if area_street:
                    address.area_street = area_street

                if locality:
                    address.locality = locality

                if city:
                    address.city = city

                if state:
                    address.state = state

                if pincode:
                    address.pincode = pincode

                if country:
                    address.country = country

                if contact_name:
                    address.contact_name = contact_name

                if contact_no:
                    address.contact_no = contact_no

                if address_type:
                    address.address_type = address_type

                if is_default is not None:
                    if is_default:
                        Address.objects.filter(user=request.user,is_deleted=False).update(is_default=False)

                    address.is_default = is_default

                address.updated_by = request.user
                address.updated_at = timezone.now()
                address.save()

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Address Updated Successfully",
                "data": {
                    "address_id": address.id,
                    "house_no": address.house_no,
                    "area_street": address.area_street,
                    "locality": address.locality,
                    "city": address.city,
                    "state": address.state,
                    "pincode": address.pincode,
                    "country": address.country,
                    "contact_name": address.contact_name,
                    "contact_no": address.contact_no,
                    "address_type": address.address_type,
                    "is_default": address.is_default,
                    "full_address": f"{address.house_no}, {address.area_street}, {address.locality}, {address.city}, {address.state} - {address.pincode}"
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Address.DoesNotExist:
            return Response({"status": "fail", "message": f"{NOT_FOUND} - Address not found"},
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"status": "error", "message": f"{INTERNAL_SERVER_ERROR} - {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request):
        try:
            address_id = request.query_params.get('address_id')

            missing = check_missing_fields(request.query_params, ['address_id'])
            if missing:
                return missing

            int_error = integer_field_validator(request, ['address_id'], source="params")
            if int_error:
                return int_error

            address = Address.objects.get(id=address_id, is_deleted=False)
            
            if address.user != request.user:
                return Response({'status': 'fail', 'message': f'{UNAUTHORIZED} - Unauthorized access'}, 
                                status=status.HTTP_403_FORBIDDEN)
                            
            with transaction.atomic():
                address.is_deleted = True
                address.save()
                
                if address.is_default:
                    new_default = Address.objects.filter(user=request.user, is_deleted=False).exclude(id=address.id).first()
                    if new_default:
                        new_default.is_default = True
                        new_default.save()

                response_data = {
                    'status': 'success',
                    'message': f'{SUCCESS} - Address Deleted Successfully'
                }
                return Response(response_data, status=status.HTTP_200_OK)

        except Address.DoesNotExist:
            return Response({'status': 'fail', 'message': f'{NOT_FOUND} - Address not found.'}, 
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def set_default_address(self, request):
        try:
            address_id = request.data.get("address_id")
            
            required = ['address_id']
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing
            
            int_error = integer_field_validator(request, ['address_id'])
            if int_error:
                return int_error

            address = Address.objects.get(id=address_id, is_deleted=False)
            
            if address.user != request.user:
                return Response({'status': 'fail', 'message': f'{UNAUTHORIZED} - Unauthorized access'}, 
                                status=status.HTTP_403_FORBIDDEN)
                
            Address.objects.filter(user=request.user, is_deleted=False).update(is_default=False)

            with transaction.atomic():
                address.is_default = True
                address.save()
            
            return Response({'status': 'success','message': f'{SUCCESS} - Default address updated successfully'}, 
                            status=status.HTTP_200_OK)
        
        except Address.DoesNotExist:
            return Response({'status': 'fail', 'message': f'{NOT_FOUND} - Address not found'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)