#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

import inspect

# Global rooms list

g_rooms_list = []


# Debugging only

def dbg_lno():

    return inspect.currentframe().f_back.f_lineno


# Room class

class Room:

    def __init__(self, room_data):# process input data

        print ('\t', room_data)

        self.room_no = self.get_room_num(room_data[0])

        self.floor = self.get_floor(room_data[0])

        self.capacity = room_data[1]

        self.bk_time_dict = {}

        times_list = room_data[2:]

        self.process_time_data(times_list)

    def get_floor(self, room_id):

        room_info = room_id.split('.')

        if len(room_id) <= 1:

            print ('ERROR: get_floor ->', dbg_lno())

            return None

        return room_info[0]

    def get_room_num(self, room_id):

        room_info = room_id.split('.')

        if len(room_info) <= 1:

            print ('ERROR: get_room_num ->', dbg_lno())

            return None

        return room_info[1]

    def get_room_capacity(self):

        return int(self.capacity)

    def get_room_info(self):

        # print('ROOM=', self.room_no, ' floor=', self.floor, ' capacity=', self.capacity)

        print (
            '\t(',
            self.floor,
            '.',
            self.room_no,
            ') capacity =',
            self.capacity,
            )

        print ('\tbooking_times dict=', self.bk_time_dict)

    def get_booking_times(self):

        for (key, value) in self.bk_time_dict.items():

            print (key, value)

    def add_booking_time(self, str_start_time, str_end_time):

        dtm_start = datetime.datetime.now()

        dtm_end = datetime.datetime.now()

        start_tm_lst = str_start_time.split(':')

        if len(start_tm_lst) <= 1:

            print ('ERROR: add_booking_time ->', dbg_lno())

            return None

        end_tm_lst = str_end_time.split(':')

        if len(end_tm_lst) <= 1:

            print ('ERROR: add_booking_time ->', dbg_lno())

            return None

        n_dt_start = dtm_start.replace(microsecond=0, second=0,
                hour=int(start_tm_lst[0]), minute=int(start_tm_lst[1]))

        n_dt_end = dtm_end.replace(microsecond=0, second=0,
                                   hour=int(end_tm_lst[0]),
                                   minute=int(end_tm_lst[1]))

        # print(dtm_start,' --> ', dtm_end)

        # self.bk_time_dict[n_dt_start] = n_dt_end

        # key, value where key=mtg_start and value=[mtg_eng]

        self.bk_time_dict[n_dt_start] = [n_dt_end, False]

    def process_time_data(self, str_times):

        i = j = 0

        for i in range(0, len(str_times), 2):

            j = i + 1

            if j >= len(str_times):

                break

            # add to room obj

            self.add_booking_time(str_times[i], str_times[j])

    def reserve_time_slot(
        self,
        room_idx,
        dt_key,
        val=True,
        ):

        val_list = g_rooms_list[room_idx].bk_time_dict[dt_key]

        if len(val_list) != 2:

            print ('ERROR: time_slot data error')
        else:

            val_list[1] = val


class RoomScheduler:

    def __init__(self):

        print ('\nStarting RoomScheduler')

        print ('%d rooms are init') % len(g_rooms_list)

    def get_avail_multi_room(
        self,
        num_team_mtg,
        floor_team_mtg,
        n_schd_dt_start,
        n_schd_dt_end,
        ):

        global g_rooms_list

        room_is_found = False

        one_pass = False

        done = False

        last_saved_val_list = []

        resv_rms = []

        i = 0

        while i < len(g_rooms_list) and done == False:

            if g_rooms_list[i].get_room_capacity() >= int(num_team_mtg):

                # check the available time timeslots for each room

                for (index, key) in \
                    enumerate(g_rooms_list[i].bk_time_dict):

                    val_list = g_rooms_list[i].bk_time_dict[key]

                    # check if the meeting can terminate without another room

                    if one_pass == False and key <= n_schd_dt_start \
                        and val_list[0] >= n_schd_dt_end \
                        and val_list[1] != True:

                        room_is_found = True

                        last_saved_val_list = val_list

                        resv_rms.append(g_rooms_list[i])

                        g_rooms_list[i].reserve_time_slot(i, key, True)

                        # check if its the last needed slot

                        if val_list[0] >= n_schd_dt_end:

                            done = True

                        break
                    elif one_pass == True and key <= n_schd_dt_start \
                        and val_list[1] != True:

                    # intermediate room checking

                        # check the next slot

                        if val_list[0] < n_schd_dt_end and val_list[0] \
                            < n_schd_dt_start:

                            # slot is too early, ignore it

                            continue

                        # we can use this imtermediate roon

                        room_is_found = True

                        last_saved_val_list = val_list

                        resv_rms.append(g_rooms_list[i])

                        g_rooms_list[i].reserve_time_slot(i, key, True)

                        # check if its the last needed slot

                        if val_list[0] >= n_schd_dt_end:

                            done = True

                        break

                # end for loop for slot (dict) search

                # now adjust the remaining time for the next room

                if done == False and room_is_found == True:

                    cur_room_end_time = last_saved_val_list[0]

                    if n_schd_dt_end > cur_room_end_time and one_pass \
                        == True:

                        # we need another unreserved room, set the new start time for the search

                        n_schd_dt_start = cur_room_end_time

                        # continue search

                        room_is_found = False

                        # force start again, since end time changed.

                        i = 0

                        continue
                    else:

                        room_is_found = True

                        done = True

            # inc index to continue search

            i += 1

            # mark one_pass is over

            if i >= len(g_rooms_list):

                # rooms are scanned once, mark it

                if one_pass == False:

                    one_pass = True

                    # force one more pass

                    i = 0

            # end if room capacity check

        # endfor loop

        if done == False and room_is_found == False:

            print ('Not all rooms found')

        # return available rooms

        return resv_rms

    def schdl_multi_room(self, inp):

        inp_data_list = inp.rstrip().split(',')  # using rstrip to remove the \n

        print ('INPUT: inp_data_list=', inp_data_list)

        num_team_mtg = inp_data_list[0]

        floor_team_mtg = inp_data_list[1]

        schd_start = datetime.datetime.now()

        schd_end = datetime.datetime.now()

        schd_start_tm_lst = inp_data_list[2].split(':')

        schd_end_tm_lst = inp_data_list[3].split(':')

        n_schd_dt_start = schd_start.replace(microsecond=0, second=0,
                hour=int(schd_start_tm_lst[0]),
                minute=int(schd_start_tm_lst[1]))

        n_schd_dt_end = schd_end.replace(microsecond=0, second=0,
                hour=int(schd_end_tm_lst[0]),
                minute=int(schd_end_tm_lst[1]))

        resv_rms = self.get_avail_multi_room(num_team_mtg,
                floor_team_mtg, n_schd_dt_start, n_schd_dt_end)

        if resv_rms == None:

            print ('No rooms are avail')

            return None
        else:

            print ('Scheduled rooms:')

        return resv_rms


# DB reader

def read_input_file(file_name):

    idx = 0

    global g_rooms_list

    file = open(file_name, 'r')

    print ('Input room table:')

    for line in file.readlines():

        # handle comments and whitespace

        line.strip()

        if line == '' or line.startswith('#'):

            continue

        # using rstrip to remove the \n

        room_data = line.rstrip().split(',')

        if '' in room_data:

            continue

        # validation checks

        if '' in room_data:

            continue

        if '.' not in room_data[0]:

            continue

        if not room_data or len(room_data) < 4 or len(room_data) % 2 \
            != 0:

            continue

        # input is parsed

        print ('[', idx, ']')

        room_inst = Room(room_data)

        g_rooms_list.append(room_inst)

        idx += 1


if __name__ == '__main__':

    read_input_file('rooms.txt')

    rm_schdler = RoomScheduler()

    print ('''
--------------------
test1''')

    # 5 team members, located on the 8th floor, meeting time 10:30 - 11:30

    # Result: 9.547

    inp = '5,8,10:30,11:30'

    resv_rms = rm_schdler.schdl_multi_room(inp)

    for x in range(len(resv_rms)):

        resv_rms[x].get_room_info()

    # unreserve it

    print ('\nUnreserve the time slots:')

    dtm_start = datetime.datetime.now()

    n_dt_start = dtm_start.replace(microsecond=0, second=0, hour=10,
                                   minute=30)

    resv_rms[x].reserve_time_slot(7, n_dt_start, False)

    resv_rms[x].get_room_info()

    print ('''
--------------------
test2''')

    # 9,7,15:30,16:00 # 9 team members, located on the 7th floor, meeting time 15:30 - 16:00

    # Result: 6.10

    inp = '9,7,15:30,16:00'

    resv_rms = rm_schdler.schdl_multi_room(inp)

    for x in range(len(resv_rms)):

        resv_rms[x].get_room_info()

    # unreserve it

    print ('\nUnreserve the time slots:')

    dtm_start = datetime.datetime.now()

    n_dt_start = dtm_start.replace(microsecond=0, second=0, hour=15,
                                   minute=15)

    resv_rms[x].reserve_time_slot(5, n_dt_start, False)

    resv_rms[x].get_room_info()

    print ('''
--------------------
test3''')

    # input example: [15,9,12:00,18:00]

    # Result: 9.312, 7.348, 4.249

    inp = '15,9,12:00,18:00'

    resv_rms = rm_schdler.schdl_multi_room(inp)

    if resv_rms == None:

        print ('No room available')
    else:

        for x in range(len(resv_rms)):

            resv_rms[x].get_room_info()

        # unreserve the rooms now.

        print ('\nUnreserve the time slots:')

        dtm_start = datetime.datetime.now()

        n_dt_start = dtm_start.replace(microsecond=0, second=0,
                hour=16, minute=30)

        resv_rms[0].reserve_time_slot(9, n_dt_start, False)

        n_dt_start = dtm_start.replace(microsecond=0, second=0,
                hour=13, minute=30)

        resv_rms[0].reserve_time_slot(7, n_dt_start, False)

        n_dt_start = dtm_start.replace(microsecond=0, second=0,
                hour=17, minute=30)

        resv_rms[0].reserve_time_slot(10, n_dt_start, False)

        # after unreserving

        for x in range(len(resv_rms)):

            resv_rms[x].get_room_info()

    print ('''
--------------------
test4''')

    # 5 team members, located on the 8th floor, meeting time 10:30 - 11:30

    # Result: 9.547

    inp = '5,8,10:30,11:30'

    resv_rms = rm_schdler.schdl_multi_room(inp)

    for x in range(len(resv_rms)):

        resv_rms[x].get_room_info()

    # unreserve it

    print ('\nUnreserve the time slots:')

    dtm_start = datetime.datetime.now()

    n_dt_start = dtm_start.replace(microsecond=0, second=0, hour=10,
                                   minute=30)

    resv_rms[x].reserve_time_slot(7, n_dt_start, False)

    resv_rms[x].get_room_info()

    print ('''
--------------------
test5''')

    # 9,7,15:30,16:00 # 9 team members, located on the 7th floor, meeting time 15:30 - 16:00

    # Result: Room 6.10

    inp = '9,7,15:30,16:00'

    resv_rms = rm_schdler.schdl_multi_room(inp)

    for x in range(len(resv_rms)):

        resv_rms[x].get_room_info()

    # unreserve it

    print ('\nUnreserve the time slots:')

    dtm_start = datetime.datetime.now()

    n_dt_start = dtm_start.replace(microsecond=0, second=0, hour=15,
                                   minute=15)

    resv_rms[x].reserve_time_slot(5, n_dt_start, False)

    resv_rms[x].get_room_info()

    print ('''
--------------------
test6''')

    # input example: [15,9,12:00,18:00]

    # Result: 9.312, 7.348, 4.249

    inp = '7,9,9:00,16:00'

    resv_rms = rm_schdler.schdl_multi_room(inp)

    if resv_rms == None:

        print ('No room available')
    else:

        for x in range(len(resv_rms)):

            resv_rms[x].get_room_info()

        # unreserve the rooms now.

        print ('\nUnreserve the time slots:')

        dtm_start = datetime.datetime.now()

        n_dt_start = dtm_start.replace(microsecond=0, second=0, hour=9,
                minute=0)

        resv_rms[0].reserve_time_slot(2, n_dt_start, False)

        n_dt_start = dtm_start.replace(microsecond=0, second=0, hour=9,
                minute=15)
				
		resv_rms[0].reserve_time_slot(5, n_dt_start, False)

        # # after unreserving

        for x in range(len(resv_rms)):

            resv_rms[x].get_room_info()