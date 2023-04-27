reply = (
    "{job_name} image using prompt:\n**{prompt}**\n"
    "\n"
    "Position in queue: {position} ({{status}})\n"
    "\n"
    "by [@{username}](tg://user?id={user_id})"
)


class Queue:
    def __init__(self):
        self.tasks = []

    def get_position(self, job_id):
        return self.tasks.index(job_id)

    def enqueue(self, job_id):
        self.tasks.append(job_id)

    def dequeue(self):
        return self.tasks.pop(0)

    def wait_for_completion(self, job_id, job_name, prompt, username, user_id):
        job_index = self.get_position(job_id)
        while self.tasks[0] != job_id:
            prev_job_index = job_index
            job_index = self.get_position(job_id)
            if prev_job_index != job_index:
                print(
                    reply.format(
                        job_name=job_name,
                        prompt=prompt,
                        position=job_index,
                        status="Pending",
                        username=username,
                        user_id=user_id,
                    )
                )
        print(
            reply.format(
                job_name=job_name,
                prompt=prompt,
                position=job_index,
                status="Processing",
                username=username,
                user_id=user_id,
            )
        )


# q = Queue()

# some_work = "asd"
# some_work2 = "asaaad"

# q.enqueue(some_work)
# q.wait_for_completion(some_work, "Generating", "lol", "duuuuuuuden", "123")
# q.enqueue(some_work2)
# q.dequeue()
# q.wait_for_completion(some_work2, "Generating", "lol", "duuuuuuuden", "123")
# q.dequeue()
# print("Done")
